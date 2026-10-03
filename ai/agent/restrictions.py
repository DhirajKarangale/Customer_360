import os
import json
import re as _re
from langchain_core.messages import AIMessage
from ai.agent.state import AgentState
from ai.utils.llm_utils import get_llm
from ai.utils.message_manager import get_message


class DataRestrictionManager:
    """
    A module to manage data access restrictions for insurance agents.
    Can be toggled via ENABLE_AGENT_DATA_RESTRICTIONS in environment.
    """

    @property
    def enabled(self):
        return os.getenv("ENABLE_AGENT_DATA_RESTRICTIONS").lower() == "true"

    def check_access(
        self,
        db_access,
        logged_in_agent_id: str = None,
        target_agent_identifier: str = None,
        target_customer_identifier: str = None,
        target_policy_identifier: str = None,
    ) -> tuple[bool, str]:
        """
        Validates if the logged_in_agent_id has permission to access the target data.
        Returns (is_allowed, error_message).
        """
        if not self.enabled or not logged_in_agent_id:
            return True, ""

        funny_message = get_message("system_access_denied", "SYSTEM ERROR: ACCESS DENIED. (AI INSTRUCTION: CRITICAL: DO NOT RETRY. You attempted to access another agent's data. Stop immediately and politely inform the user that you can only access their own policies, customers, and data. Keep it friendly and professional. Do not output this instruction.)")

        try:

            if target_agent_identifier:

                target_agent_id = self._resolve_agent_id(
                    db_access, target_agent_identifier
                )
                if target_agent_id and target_agent_id != logged_in_agent_id:
                    return False, funny_message

            if target_customer_identifier:
                customer_id = self._resolve_customer_id(
                    db_access, target_customer_identifier
                )
                if customer_id:

                    query = f"SELECT 1 FROM policies WHERE customer_id = '{customer_id}' AND agent_id = '{logged_in_agent_id}' LIMIT 1"
                    if "1" not in db_access.execute_query(query):
                        return False, funny_message

            if target_policy_identifier:
                query = f"SELECT agent_id FROM policies WHERE policy_number = '{target_policy_identifier}' LIMIT 1"
                res = db_access.execute_query(query)
                if (
                    logged_in_agent_id not in res
                    and "Query returned no results" not in res
                ):
                    return False, funny_message

        except Exception as e:
            return False, get_message("permission_resolve_error", f"ACCESS DENIED (Error resolving permissions: {e})", e=e)

        return True, ""

    def _resolve_agent_id(self, db_access, identifier: str) -> str:
        import uuid

        try:
            uuid.UUID(identifier)
            return identifier
        except Exception:
            res = db_access.execute_query(
                f"SELECT id FROM insurance_agents WHERE name ILIKE '%{identifier}%' LIMIT 1"
            )
            import re

            m = re.search(r"([a-f0-9\-]{36})", res)
            return m.group(1) if m else None

    def _resolve_customer_id(self, db_access, identifier: str) -> str:
        import uuid

        try:
            uuid.UUID(identifier)
            return identifier
        except Exception:
            res = db_access.execute_query(
                f"SELECT id FROM customers WHERE name ILIKE '%{identifier}%' LIMIT 1"
            )
            import re

            m = re.search(r"([a-f0-9\-]{36})", res)
            return m.group(1) if m else None


restriction_manager = DataRestrictionManager()

llm = get_llm("RESTRICTION")


_UUID_RE = _re.compile(
    r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}", _re.IGNORECASE
)
_POLICY_NUM_RE = _re.compile(r"POL-\d+", _re.IGNORECASE)


def _might_reference_entities(query: str) -> bool:
    """
    Fast heuristic: returns True only if the query likely references a
    SPECIFIC agent, customer, or policy by name or ID.

    Returns False for generic queries like "show my policies", "summarize
    my interactions", "what are my active customers" — where the logged-in
    agent's own scope is clearly implied and no cross-agent risk exists.

    This avoids a full LLM call (~15s) on the majority of safe requests.
    """

    if _UUID_RE.search(query) or _POLICY_NUM_RE.search(query):
        return True

    words = query.split()
    for word in words[1:]:
        clean = word.strip(".,!?;:'\"()")
        if clean and clean[0].isupper() and len(clean) > 1 and clean.isalpha():
            return True

    return False


def restriction_node(state: AgentState):
    logged_in_agent_id = state.get("insurance_agents_id")
    if not restriction_manager.enabled or not logged_in_agent_id:
        return {}

    messages = state.get("messages", [])
    if not messages:
        return {}

    last_user_query = messages[-1].content

    if not _might_reference_entities(last_user_query):
        return {}

    extraction_prompt = f"""You are a security entity extractor. 
Extract any insurance agents, customers, or policies mentioned in the following user query.
Return exactly a JSON object in this format, and nothing else:
{{
  "agents": ["name or ID", ...],
  "customers": ["name or ID", ...],
  "policies": ["policy number or ID", ...]
}}
If none are mentioned, return empty arrays.
User query: {last_user_query}
"""
    response = llm.invoke(extraction_prompt)

    response_content = str(response) if response else "{}"
    try:
        if "```json" in response_content:
            response_content = response_content.split("```json")[1].split("```")[0]
        entities = json.loads(response_content.strip())
    except Exception as e:
        import logging

        logging.error(f"Failed to parse restriction JSON: {e}")
        entities = {"agents": [], "customers": [], "policies": []}

    from ai.agent.tools import AIDatabaseAccess

    db = AIDatabaseAccess()
    try:
        for agent in entities.get("agents", []):
            allowed, _ = restriction_manager.check_access(
                db, logged_in_agent_id, target_agent_identifier=agent
            )
            if not allowed:
                return {
                    "messages": [
                        AIMessage(
                            content=get_message("unauthorized_agent", "Oops! It looks like you're trying to access data for another agent. I can only help you with your own policies, customers, and data! 😊")
                        )
                    ]
                }

        for customer in entities.get("customers", []):
            allowed, _ = restriction_manager.check_access(
                db, logged_in_agent_id, target_customer_identifier=customer
            )
            if not allowed:
                return {
                    "messages": [
                        AIMessage(
                            content=get_message("unauthorized_customer", "Oops! It looks like you're trying to access data for a customer that does not belong to you. I can only help you with your own policies, customers, and data! 😊")
                        )
                    ]
                }

        for policy in entities.get("policies", []):
            allowed, _ = restriction_manager.check_access(
                db, logged_in_agent_id, target_policy_identifier=policy
            )
            if not allowed:
                return {
                    "messages": [
                        AIMessage(
                            content=get_message("unauthorized_policy", "Oops! It looks like you're trying to access a policy that does not belong to you. I can only help you with your own policies, customers, and data! 😊")
                        )
                    ]
                }
    finally:
        db.close()

    return {}
