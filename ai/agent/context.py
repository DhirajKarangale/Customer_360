from ai.agent.state import AgentState

def resolve_names_from_state(state: AgentState) -> tuple[str, bool]:
    """
    Opens a SINGLE DB connection to resolve agent name, customer name, and
    policy number from UUIDs in the state. Returns (context_string, has_context).
    Significantly cheaper than opening 3 separate connections.
    """
    import ai.agent.state
    from ai.agent.tools import AIDatabaseAccess

    agent_uuid = state.get("insurance_agents_id")
    cust_uuid = state.get("customers_id")
    pol_uuid = state.get("policies_id")

    if not agent_uuid and not cust_uuid and not pol_uuid:
        return "", False

    context_lines = []
    has_context = False

    db = AIDatabaseAccess()
    try:
        if agent_uuid:
            try:
                res = db.execute_query(
                    f"SELECT name FROM insurance_agents WHERE id = '{agent_uuid}'"
                )
                lines = [
                    l.strip()
                    for l in res.splitlines()
                    if l.strip() and not l.startswith("-")
                ]
                agent_name = (
                    lines[1]
                    if len(lines) > 1 and lines[0].lower() == "name"
                    else "Unknown Agent"
                )
            except Exception:
                agent_name = "Unknown Agent"
            context_lines.append(f"- Logged-in Agent ID: {agent_uuid}")
            context_lines.append(f"- Logged-in Agent Name: {agent_name}")
            has_context = True
            ai.agent.state.CURRENT_AGENT_ID = agent_uuid

        if cust_uuid:
            try:
                res = db.execute_query(
                    f"SELECT name FROM customers WHERE id = '{cust_uuid}'"
                )
                lines = [
                    l.strip()
                    for l in res.splitlines()
                    if l.strip() and not l.startswith("-")
                ]
                cust_name = (
                    lines[1]
                    if len(lines) > 1 and lines[0].lower() == "name"
                    else "Unknown Customer"
                )
            except Exception:
                cust_name = "Unknown Customer"
            context_lines.append(f"- Active Customer ID: {cust_uuid}")
            context_lines.append(f"- Active Customer Name: {cust_name}")
            has_context = True

        if pol_uuid:
            try:
                res = db.execute_query(
                    f"SELECT policy_number FROM policies WHERE id = '{pol_uuid}'"
                )
                lines = [
                    l.strip()
                    for l in res.splitlines()
                    if l.strip() and not l.startswith("-")
                ]
                pol_number = (
                    lines[1]
                    if len(lines) > 1 and lines[0].lower() == "policy_number"
                    else "Unknown Policy"
                )
            except Exception:
                pol_number = "Unknown Policy"
            context_lines.append(f"- Active Policy ID: {pol_uuid}")
            context_lines.append(f"- Active Policy Number: {pol_number}")
            has_context = True

    finally:
        db.close()

    context_str = (
        "\n[Current Session Context]\n" + "\n".join(context_lines)
        if context_lines
        else ""
    )
    return context_str, has_context
