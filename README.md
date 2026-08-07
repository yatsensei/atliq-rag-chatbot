# 🏢 AtliQ Corp Internal AI Assistant (Enterprise RAG Pipeline)

An enterprise-grade Retrieval-Augmented Generation (RAG) system built to securely query internal company documents. This project goes beyond a basic LLM wrapper by implementing strict Role-Based Access Control (RBAC), Personal Identifiable Information (PII) redaction, and automated metric evaluation.

## 🌟 Key Features

* **Role-Based Access Control (RBAC):** Users can only retrieve documents authorized for their specific department (e.g., Finance cannot access HR payroll data). Handled natively at the vector database level using Qdrant payload filters.
* **PII Guardrails:** Utilizes Microsoft Presidio NLP to scrub sensitive information (names, emails, phone numbers) from retrieved documents *before* they are sent to the LLM context window.
* **Prompt Injection Defense:** Pre-processing validation blocks malicious jailbreak attempts and out-of-scope queries.
* **Automated Evaluation:** Integrated with the Ragas framework to mathematically prove AI accuracy (achieving 1.00 Faithfulness and 1.00 Context Recall).
* **Cost Tracking & Observability:** Real-time token cost estimation displayed in the Streamlit UI, with full backend tracing powered by LangSmith.

## 🖥️ Interface

The Streamlit front end is styled as an internal enterprise console: a role-scoped
workspace, per-answer citations, and live governance telemetry in the sidebar.

| Workspace overview | Grounded answer with citations |
| --- | --- |
| ![Workspace overview](docs/screenshots/01-workspace-overview.png) | ![Grounded answer](docs/screenshots/02-grounded-answer-citations.png) |

| RBAC boundary enforced | Prompt injection blocked |
| --- | --- |
| ![RBAC boundary](docs/screenshots/04-rbac-access-boundary.png) | ![Injection blocked](docs/screenshots/07-prompt-injection-blocked.png) |

Every response carries its retrieval status, latency, estimated cost and the exact
source documents it was built from. The sidebar shows the departments the active
role may search, the documents indexed for it, and the state of each guardrail.

More screenshots — including the Finance and Executive workspaces — live in
[`docs/screenshots/`](docs/screenshots).

## 🛠️ Tech Stack

* **LLM:** Llama 3.1 8B (via Groq API for ultra-low latency)
* **Vector Database:** Qdrant (Dockerized)
* **Embeddings:** HuggingFace `all-MiniLM-L6-v2`
* **Framework:** LangChain & Python
* **Frontend:** Streamlit
* **Security & Eval:** Microsoft Presidio, Ragas, Pytest

## 🚀 How to Run Locally

**1. Clone the repository and install dependencies:**
```bash
git clone [https://github.com/yourusername/atliq-rag-chatbot.git](https://github.com/yourusername/atliq-rag-chatbot.git)
cd atliq-rag-chatbot
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt