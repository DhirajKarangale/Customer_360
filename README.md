# 🎯 Customer 360 & Next Best Action Engine 

<div align="center">
  <img src="https://img.shields.io/badge/Snowflake-CoCo_Hackathon-blue?style=for-the-badge&logo=snowflake" alt="Snowflake Hackathon" />
  <img src="https://img.shields.io/badge/Status-Deployed-success?style=for-the-badge" alt="Status" />
</div>

<p align="center">
  <strong>An enterprise-ready AI application providing a unified 360-degree customer view for insurers and lenders.</strong>
</p>

## 🔗 Live Demo
**[Customer 360 Web Application](https://customer360-theta.vercel.app/)**

### 🔐 Demo Accounts
You can test the application using the following demo credentials:
- **Emails:** `suresh.d@dcoders.com` | `neha.k@dcoders.com`
- **Password:** `Pass@123`

---

## 📖 Project Overview
Insurers and lenders require a unified customer view to personalize interactions, underwrite smarter, and reduce churn. **Customer 360** seamlessly combines structured policy data with unstructured customer touchpoints (e.g., call transcripts, documents) to deliver comprehensive insights. 

Leveraging cutting-edge Agentic frameworks and **Snowflake**, this solution automatically generates sentiment analysis, highlights personalization opportunities, and recommends the **Next Best Action** for agents to act on.

---

## ✨ Key Features
- **Unified 360° Customer Dashboard**: Move from a customer question to a recommended action in a single, intuitive experience.
- **Next Best Action Engine**: AI-driven suggestions tailored to each customer's specific profile, interactions, and policies.
- **Asynchronous AI Workflows**: Handles long-running generative tasks through a scalable worker queue using Redis Streams.
- **Enterprise-ready Architecture**: Secure JWT-based authentication, separated frontend and backend, with a dedicated AI worker.
- **Snowflake Integration**: Uses Snowflake for robust data handling, semantic models, and retrieval pipelines.

---

## 🏗️ Architecture & Technologies Used

Our architecture is split into three main microservices:

### 1. Frontend (Web Application)
A modern, highly responsive React web interface providing the agent portal.
- **Framework**: React 19, Vite
- **Styling & UI**: Tailwind CSS v4, Shadcn UI, Framer Motion (for dynamic micro-animations)
- **State Management**: Zustand
- **Routing**: React Router v7
- **Data Visualization**: Recharts

### 2. Backend (API Gateway)
A fast, robust REST API that connects the frontend to the database and orchestrates AI tasks.
- **Framework**: FastAPI (Python)
- **Authentication**: PyJWT (Secure Bearer Tokens), Passlib (Bcrypt)
- **Database Connection**: Snowflake Connector, Psycopg2 (PostgreSQL)
- **Task Delegation**: Redis (for queuing asynchronous LLM processing jobs)

### 3. AI Worker (Agentic Workflow Service)
A dedicated background worker service tailored for intensive language modeling and RAG tasks.
- **Frameworks**: LangGraph, LangChain
- **LLMs**: Google GenAI, Groq
- **Vector Search / RAG**: FAISS
- **Queue Consumer**: Redis Streams consumer ensuring reliable job execution and callbacks.

---

## ⚙️ Snowflake CoCo Capabilities Demonstrated
As required by the Snowflake CoCo Hackathon (GCC Edition), CoCo capabilities are embedded across the solution lifecycle:
- **Data Processing**: Using Snowflake to query structured/semi-structured customer data and store unstructured documents.
- **AI Agent Orchestration**: Connecting LLM architectures with enterprise data securely.
- **Semantic Data Models**: Querying semantic views of customer, policy, and claims data directly from the AI agents.

---

## 🚀 Local Setup & Installation

### Prerequisites
- Node.js (v18+)
- Python (3.10+)
- Redis Server
- Snowflake Account

### 1. Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

### 2. Backend Setup
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Configure your .env file with appropriate keys
# RUN the server:
uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
```

### 3. AI Worker Setup
```bash
cd ai
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Configure your .env file with Snowflake, LLM, and Redis credentials
# RUN the worker:
python worker.py
```

---

## 📄 License
This project was developed for the **Snowflake CoCo CLI Hackathon 2026 – GCC Edition**.