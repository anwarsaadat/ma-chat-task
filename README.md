# Multi-Agent Chat System

This repository contains a modular multi-agent orchestration system designed for collaborative task execution, memory persistence, and adaptive reasoning. The system leverages Docker for portability and includes optional integration with LLMs (Groq or others).

---

## 🚀 Architecture Overview

The system consists of three main layers:

1. **Coordinator**  
   - Routes tasks to specialized agents.  
   - Handles dependency resolution and workflow sequencing.  
   - Ensures logs and decision traces are captured.

2. **Agents (Specialized Workers)**  
   - **Classifier Agent** → Categorizes tasks.  
   - **Executor Agent** → Runs actions, retrieves or computes results.  
   - **Summarizer Agent** → Synthesizes outputs for reporting.  

3. **Memory Layer (Persistence & Retrieval)**  
   - Task results are stored in a structured SQLite database.  
   - Retrieval queries are agent-aware for adaptive reuse.  
   - Includes fallback to rule-based search if LLM is unavailable.

### ASCII Sequence Flow

```text
+-------------+        +-------------+       +-------------+       +-------------+
|   Client    |        | Orchestrator|       |   Agents    |       |   Database  |
+-------------+        +-------------+       +-------------+       +-------------+
       |                       |                     |                     |
       |  Submit Task -------->|                     |                     |
       |                       | Classify ---------->|                     |
       |                       |-------------------->| Classifier Agent    |
       |                       |                     |                     |
       |                       | Execute ----------->| Executor Agent      |
       |                       |                     |                     |
       |                       | Summarize --------->| Summarizer Agent    |
       |                       |                     |                     |
       |                       | Store/Retrieve -------------------------->|
       |                       |                     |                     |
       |   Result <------------|<--------------------|                     |
       |                       |                     |                     |
```

---

## 🛠️ Running the System

## Method 1

### 1. Clone the Repository
```bash
git clone https://github.com/anwarsaadat/ma-chat-task.git
cd ma-chat-task
```

### 2. Build with Docker
```bash
make build
```

### 3. Run the Service
```bash
make run
```

### 4. Run Tests
```bash
make test
```

*If permission issue arises, then use ```sudo``` before the command. Like, ```sudo make build```

---

## Method 2

If ```make``` command doesn't work, then use below alternative commands to run and test the application.

### 1. Build with Docker
```bash
docker build -t ma-chat .
```

### 2. Run the Service
```bash
sudo docker run -it --rm -e PYTHONPATH=/app/src ma-chat
```

### 4. Run Tests
```bash
sudo docker run -it --rm -e PYTHONPATH=/app ma-chat python -m pytest -q
```

---

## 🧠 Memory Design & Retrieval

- **Database**: SQLite (lightweight, portable).
- **Schema**:
  - `tasks (id, type, input, output, timestamp)`
- **Retrieval Strategy**:
  - Recent matching tasks are retrieved first.  
  - Agents adaptively reuse results where applicable.  
  - If LLM is configured → semantic retrieval.  
  - If LLM unavailable → rule-based keyword matching.

---

## 🤖 LLM Integration (Optional)

- **Provider**: [Groq](https://console.groq.com/docs/overview) Free Developer Tier.  
- **Usage**:
  - Classification  
  - Summarization  
  - Task Decomposition  

**Fallback**:  
If the LLM is unavailable, the system switches to rule-based logic to ensure uninterrupted functionality.

---

## 📂 Repository Structure

```
multi-agent-system/
├── agents/              # Specialized agents
├── core/                # Coordinator logic
├── memory/              # Database + retrieval layer
├── tests/               # Unit tests
├── Dockerfile
├── makefile
└── README.md
```

---

## 🌍 Portability

Since the system is fully containerized with **Docker**, it runs consistently across any environment that supports Docker:
- Linux
- macOS
- Windows (via WSL2 or Docker Desktop)

This ensures **reproducibility anywhere in the world**.

---

## 📜 Logs & Traceability

- Logs are automatically generated for:
  - Task submissions
  - Agent routing
  - Memory retrievals
  - Errors/fallback events
- Logs are stored in `outputs/` with scenario-specific identifiers.

For Groq, you have to include your own API_KEY in .env file with name: GROQ_API_KEY