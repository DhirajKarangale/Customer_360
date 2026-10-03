SEQUENCE_GENERATION_PROMPT = """
You are an AI planning interactions. 
Customer '{customer_name}' is interacting with Insurance Agent '{agent_name}' 
regarding a {policy_type} policy (Status: {status}).
Generate a logical sequence of exactly {num_interactions} interactions using channels (Call, Email, or Chat).
OUTPUT STRICTLY A VALID JSON LIST OF STRINGS AND NOTHING ELSE. Do NOT include markdown blocks, numbers, or conversational text.
Correct format example: ["Call", "Email", "Chat", "Call", "Email"]
"""
TRANSCRIPT_GENERATION_PROMPT = """
You are an expert transcript/data generator. Write interaction #{step_num} of {total_steps} ({channel}).
Company Name: DCoders
Customer: {customer_name}
Agent: {agent_name} (Agency: {agency_name})
Policy Details: {policy_type} policy. Target end status of this policy in the system is '{status}'.
Previous context (if any): {context}
{length_desc}
CRITICAL INSTRUCTIONS TO AVOID SOUNDING LIKE A ROBOT:
{human_instructions}
- Ensure the interaction data is highly detailed, rich in context, and comprehensive.
You MUST follow the schema definitions below for your output.
Only output the raw textual data matching the {channel} schema, no extra meta commentary.
--- SCHEMA DEFINITIONS ---
{schema_prompt}
"""
SUMMARY_PROMPT = """Summarize this interaction in 1 or 2 short sentences:
{content}"""
CLEANING_PROMPT = """
You are an expert data processor. Please clean the following interaction transcript.
Apply the following cleaning rules STRICTLY without changing the user's core intent, meaning, or emotion:
1. Text Cleaning: Fix broken lines and inconsistent casing.
2. Noise Removal: Remove fillers, repetitions, and conversational noise (e.g., "Uh", "yeah"). Keep meaningful statements.
3. Semantic Normalization: Make text clear, consistent, and unambiguous.
4. Vocabulary Standardization: Use standard terms consistently.
5. Requirement Consistency: Avoid contradictory statements.
6. Ambiguity Reduction: Remove vague statements. Clearly separate knowns from unknowns.
7. Language Normalization: Convert informal spoken language into professional text. Improve grammar.
8. Context Preservation: Preserve uncertainty, suggestions, and original intent.
9. Canonicalization: Convert different representations of the same entity into a single canonical form.
10. Preserve Metadata: Do NOT remove any timestamps, participant names, headers, or roles. Preserve them exactly.
Input Transcript:
---
{text}
---
Provide ONLY the cleaned text. Do NOT include markdown formatting blocks or any conversational filler.
"""
STRUCTURING_PROMPT = """
You are an expert AI data structurer building data for a Retrieval-Augmented Generation (RAG) system.
You are given both the ORIGINAL RAW TEXT (which contains metadata like timestamps, participants, IDs) and the CLEANED TEXT (which is semantically normalized).
Structure the data into a JSON object containing "content" and "metadata".
The file type is known to be: {file_type}
The JSON MUST follow this exact structure:
{{
  "content": "<A highly summarized version of what was discussed in the interaction. Focus on the main points, questions, and decisions.>",
  "metadata": {{
    "type": "<call, chat, or email>",
    "timestamp": "<extract exact timestamp from ORIGINAL RAW TEXT. If multiple, use the first/start timestamp. Format: YYYY-MM-DDTHH:MM:SS>",
    "participants": {{
      "customer": {{
        "name": "<name of the customer from ORIGINAL RAW TEXT>",
        "id": "<customer ID (UUID) from ORIGINAL RAW TEXT>"
      }},
      "insurance_agents": [
        {{
          "name": "<agent name from ORIGINAL RAW TEXT>",
          "id": "<agent ID (UUID) from ORIGINAL RAW TEXT>"
        }}
      ]
    }},
    "user_mood": "<e.g., happy, interested, bored, frustrated, angry, confused>",
    "topics": ["<key topics discussed>"],
    "action_items": ["<any next steps or action items mentioned>"]
  }}
}}
Rules:
- You MUST accurately extract timestamps, participant names, and IDs from the ORIGINAL RAW TEXT. Do NOT invent them.
- The 'content' field should be a concise summary of the conversation, NOT the full text.
- If the user mood is not explicitly clear, infer it based on the context (e.g., neutral).
- Ensure output is STRICTLY valid JSON and nothing else. No markdown blocks like ```json.
ORIGINAL RAW TEXT:
---
{raw_text}
---
CLEANED TEXT:
---
{cleaned_text}
---
"""