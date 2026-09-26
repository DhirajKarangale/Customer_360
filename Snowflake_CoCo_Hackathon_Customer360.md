# Snowflake CoCo CLI Hackathon 2026 – GCC Edition

## 1. Hackathon Overview

- **Presented by:** Snowflake and YourStory
- **Audience:** Developers in GCC organizations based in India
- **Participation:** Solo or teams of up to 4 members
- **Goal:** Build real-world, enterprise-ready AI applications, not just prototypes.
- **Prize pool:** $10,000, plus consolation prizes
- **Evaluation focus:**
  - Real World Relevance
  - Technical Execution
  - Solution Completeness

## 2. Submission Requirements

The hackathon submission requires:

- Public GitHub repository
- Deployed, working application link
- Prototype/MVP brief
- Public demo link
- Presentation

## 3. Snowflake CoCo Requirement

CoCo is mandatory across the full solution lifecycle.

### Planning
Use CoCo to:

- Explore data
- Frame the problem
- Draft the solution design
- Define the data model
- Define ontology
- Define workflow

### Development
Use CoCo to build:

- Data pipelines
- Semantic views
- Models
- Agents
- Application code

### Execution
Use CoCo to:

- Run the complete end-to-end solution
- Orchestrate workflows
- Run scheduled/automated processes where applicable

### Testing and Validation
Use CoCo to:

- Validate outputs
- Test accuracy
- Handle errors and edge cases
- Confirm the solution behaves correctly before the demo

CoCo can be used through the **CLI or Desktop app**.

## 4. Recommended CoCo Capabilities

The hackathon recommends demonstrating:

- Synthetic data generation
- Data pipeline creation
- Semantic model and ontology authoring
- Streamlit report/application generation
- MCP connections to external tools
- Document and unstructured-data processing

Additional ways to demonstrate CoCo usage include:

- Reusable/shareable skills
- MCP connectors
- Automations and scheduled runs
- Custom tools/function calling
- Multi-agent orchestration
- Working across CoCo CLI, Desktop, and Snowsight Cloud Agents
- Guardrails and graceful fallback

## 5. Selected Problem Statement

# Customer 360 and Next Best Action Engine

### Problem

Insurers and lenders want a unified customer view to support:

- Personalization
- Smarter underwriting
- Churn reduction

### Required Solution

Build an application that combines **structured and unstructured customer touchpoints**, including call transcripts, into a unified 360-degree customer view and recommends the **Next Best Action**.

### Core Requirements

1. Unify policyholder/customer data with unstructured interactions.
2. Generate:
   - Personalization insights
   - Next Best Action recommendations
   - Sentiment insights
3. Allow the user to move from a **customer question to a recommended action in one experience**.

## 6. Data for Customer 360

The solution can use synthetic/de-identified data.

Potential data categories for the selected problem:

- Customer profiles
- Policies
- Transactions
- Claims
- Call transcripts
- Other customer interactions

The hackathon specifically recommends synthetic data so production/private customer data is not required.

## 7. AI / Agent Architecture

The hackathon allows flexibility in agent architecture.

Possible approaches include:

- Snowflake Cortex Agents
- Claude Agent SDK
- LangGraph
- Single-agent architecture
- Multi-agent architecture

LangGraph is allowed. The hackathon material also indicates that native Snowflake orchestration can receive additional recognition.

## 8. Snowflake Data and AI Capabilities

Snowflake can be used for:

- Structured customer data
- Semi-structured data
- Unstructured documents/transcripts
- Semantic views
- Cortex Search
- Cortex Analyst
- LLM/AI capabilities
- ML pipelines
- Data pipelines using streams, tasks, dynamic tables, etc.

For RAG/vector retrieval, Snowflake Cortex Search can be used with documents and unstructured data stored in Snowflake.

## 9. Application UI

The application can use a web UI such as:

- React
- Streamlit

For the selected problem, the UI can present the unified customer view and the recommended Next Best Action.

## 10. Example High-Level Flow

```text
Customer / Policy / Transaction / Claim Data
                    +
             Call Transcripts
                    ↓
              Snowflake
                    ↓
        Data Processing / RAG
                    ↓
          AI Agent / Agents
                    ↓
       Customer 360 Understanding
                    ↓
          Next Best Action
                    ↓
             React / UI
```

## 11. Important Hackathon Constraints

- CoCo must be demonstrated throughout **Planning, Development, Execution, and Testing/Validation**.
- The solution should be enterprise-oriented and complete, not only a basic prototype.
- Synthetic data can be used instead of production customer data.
- External systems can be connected through MCP.
- Agent architecture is not restricted to one specific framework.
