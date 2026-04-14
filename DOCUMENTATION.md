# Smart Manufacturing Assistant - Complete Documentation

## Table of Contents
1. [Project Overview](#project-overview)
2. [Technology Stack](#technology-stack)
3. [System Architecture](#system-architecture)
4. [File-by-File Reference](#file-by-file-reference)
5. [API Reference](#api-reference)
6. [Final Walkthrough](#final-walkthrough)

---

## Project Overview

### What Does This Project Do?

The **Smart Manufacturing Assistant** is an AI-powered application designed to help operators and engineers in a manufacturing plant. It provides:

| Feature | Description |
|---------|-------------|
| **AI Chat** | Natural language conversations about manufacturing topics |
| **Sensor Monitoring** | Real-time dashboard showing machine sensor data |
| **Fault Diagnostics** | AI analysis of sensor data to detect problems |
| **Document Retrieval** | Search and query SOPs, manuals, and procedures |
| **Spare Parts Inventory** | Track parts stock and receive scarcity alerts |
| **Log Analysis** | Upload machine logs for AI-powered performance analysis |

### Key Capabilities

1. **Multi-Agent System**: Routes queries to specialized agents (RAG, Diagnostics, General)
2. **Session-Based Memory**: Maintains conversation context across messages
3. **Safety Guardrails**: Filters unsafe and off-topic queries
4. **Local AI**: Uses Ollama/Mistral for privacy and cost savings
5. **Vector Search**: ChromaDB for semantic document retrieval

---

## Technology Stack

### Backend Technologies

| Technology | Purpose | Why This Choice? |
|------------|---------|------------------|
| **FastAPI** | Web Framework | High performance, async support, auto-documentation |
| **Ollama** | LLM Runtime | Local execution, privacy, no API costs |
| **Mistral 7B** | Language Model | Best open-source model for its size |
| **ChromaDB** | Vector Database | Embedded, zero-config, automatic persistence |
| **LangChain** | AI Framework | Standard memory, document processing tools |
| **HuggingFace** | Embeddings | Local, fast, no API needed |
| **Pandas** | Data Analysis | Industry standard for CSV processing |


### Frontend Technologies

| Technology | Purpose | Why This Choice? |
|------------|---------|------------------|
| **Streamlit** | UI Framework | Rapid Python UI development |
| **Requests** | HTTP Client | Simple API communication |

---

## Key Concepts & Implementation Details

### 1. Retrieval-Augmented Generation (RAG)

**Concept**: RAG combines the strengths of generative AI (fluent writing) with information retrieval (accuracy/facts). Instead of relying solely on the LLM's training data, RAG retrieves relevant documents from a knowledge base and feeds them into the model's context.

**Implementation**:
1. **Ingestion**: Documents are split into chunks.
2. **Indexing**: Chunks are converted to vector embeddings and stored in ChromaDB.
3. **Retrieval**: User query is converted to a vector; ChromaDB finds the closest matching chunks (Cosine Similarity).
4. **Generation**: The retrieved text is inserted into the prompt: *"Answer the user using this context: [Chunk 1]..."*

### 2. Chunking Strategy

**Concept**: LLMs have a context window limit (e.g., 4096 tokens). We cannot feed an entire manual into the prompt. Chunking breaks large documents into smaller, semantic pieces.

**Our Choice: `MarkdownHeaderTextSplitter`**
- **Why**: Traditional "character splitting" cuts text arbitrarily, often breaking sentences or separating a header from its content.
- **How it works**: It splits text based on Markdown headers (`#`, `##`, `###`).
- **Benefit**: Keeps semantic sections together. A section on "Hydraulic Maintenance" stays intact, preserving the meaning for the embedding model.
### 3. Vector Embeddings

**Concept**: Embeddings are numerical representations (lists of numbers) of text. Conceptually similar words ("King" and "Queen") appear closer together in this mathematical space than unrelated words ("King" and "Apple").

**Our Model: `all-MiniLM-L6-v2` (via HuggingFace)**
- **Dimensions**: 384-dimensional vectors.
- **Why this model**: It is a standard "Sentence Transformer" model optimized for semantic similarity. It is small (~80MB), runs very fast on local CPUs, and provides high-quality retrieval for English text.

### 4. Vector Database & Retriever

**Concept**: A Vector Database stores high-dimensional vectors and creates an index (like HNSW) for efficient similarity search.

**Our Choice: ChromaDB**
- **Type**: Embedded Vector Store.
- **Behavior**: Runs as a library inside the Python process (no separate server to manage like Pinecone or Weaviate).
- **Persistence**: Automatically saves data to the local disk (`backend/app/data/chroma_db`).
- **Retriever**: We use "Similarity Search", which finds the top `k` (default 3) vectors with the smallest angular distance (cosine distance) to the query vector.

### 5. Large Language Model (LLM)

**Concept**: The "brain" that inputs the prompt (with context) and generates the response.

**Our Choice: Mistral 7B (via Ollama)**
- **Local Runtime**: Ollama manages the model weights and provides an OpenAI-compatible API.
- **Privacy**: No data leaves the machine. Critical for manufacturing IP.
- **Cost**: $0.00 operating cost (CPU/GPU inference).
- **Latency**: No network round-trips to cloud APIs.

### 6. Multi-Agent Routing

**Concept**: Not all queries need RAG. Some are functional ("What is the temperature?"), others are conversational.

**Implementation**:
- The **Orchestrator** sends the user query to the LLM with a classification prompt.
- **Prompt**: *"Classify this query: RAG (if asking for info), DIAGNOSTICS (if asking about status), or GENERAL."*
- **Outcome**: This prevents wasting resources. We don't search the vector DB if the user just says "Hello".

---

## System Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              FRONTEND (Streamlit)                            │
│                                                                              │
│  ┌────────────┐    ┌────────────┐    ┌────────────────────┐                 │
│  │ Dashboard  │    │    Chat    │    │    Maintenance     │                 │
│  │  (sensors) │    │  (AI chat) │    │ (inventory/logs)   │                 │
│  └────────────┘    └────────────┘    └────────────────────┘                 │
│         │                │                     │                             │
│         └────────────────┼─────────────────────┘                             │
│                          │                                                   │
│                  ┌───────▼───────┐                                           │
│                  │  API Client   │                                           │
│                  └───────────────┘                                           │
└──────────────────────────┬───────────────────────────────────────────────────┘
                           │ HTTP (Port 8090)
┌──────────────────────────▼───────────────────────────────────────────────────┐
│                              BACKEND (FastAPI)                               │
│                                                                              │
│  ┌─────────────────────────────────────────────────────────────────────────┐│
│  │                            API Layer                                     ││
│  │   /sensors  │  /chat  │  /maintenance/*  │  /chat/sessions              ││
│  └─────────────────────────────────────────────────────────────────────────┘│
│                                    │                                         │
│  ┌─────────────────────────────────▼───────────────────────────────────────┐│
│  │                           Orchestrator                                   ││
│  │  • Guardrail Validation  • Query Routing  • Agent Execution             ││
│  └──────────────────────────────────────────────────────────────────────────┘
│                                    │                                         │
│  ┌─────────────────────────────────▼───────────────────────────────────────┐│
│  │                             Services                                     ││
│  │  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐           ││
│  │  │   LLM   │ │   RAG   │ │ Memory  │ │Guardrail│ │Inventory│           ││
│  │  │ Service │ │ Service │ │ Service │ │ Service │ │ Service │           ││
│  │  └─────────┘ └─────────┘ └─────────┘ └─────────┘ └─────────┘           ││
│  │  ┌─────────┐                                                            ││
│  │  │Simulator│                                                            ││
│  │  └─────────┘                                                            ││
│  └──────────────────────────────────────────────────────────────────────────┘
└──────────────────────────────────────────────────────────────────────────────┘
                    │                               │
        ┌───────────▼───────────┐       ┌───────────▼───────────┐
        │   Ollama (Mistral)    │       │       ChromaDB        │
        │   Local LLM Server    │       │   Vector Database     │
        └───────────────────────┘       └───────────────────────┘
```

---

---

## Sequential Execution Flow

The following block diagram illustrates the step-by-step lifecycle of a user request as it flows through the system.

```mermaid
flowchart TD
    %% Nodes
    User([User])
    UI[Frontend UI]
    API[Backend API]
    ORC[Orchestrator]
    GR{Guardrail Check}
    MEM_IN[Memory: Save Input]
    ROUTER{Routing Logic}
    
    %% Agents
    RAG_AG[RAG Agent]
    DIAG_AG[Diagnostics Agent]
    GEN_AG[General Agent]
    
    %% External/Services
    VEC[(ChromaDB)]
    SENS[Sensor Simulator]
    LLM[LLM Service]
    MEM_OUT[Memory: Save Output]
    
    %% Flow
    User -->|1. Types Message| UI
    UI -->|2. POST /chat| API
    API -->|3. Forward Request| ORC
    
    ORC -->|4. Validate| GR
    GR -- Blocked -->|Reject| UI
    
    GR -- Passed -->|5. Store User Msg| MEM_IN
    MEM_IN -->|6. Classify Intent| ROUTER
    
    %% Routing Paths
    ROUTER -- "Asking for Info" --> RAG_AG
    ROUTER -- "Machine Status" --> DIAG_AG
    ROUTER -- "Chitchat" --> GEN_AG
    
    %% Execution Details
    subgraph Execution_Layer [Agent Execution]
        direction TB
        RAG_AG -->|7a. Retrieve Docs| VEC
        VEC -->|Context| RAG_AG
        
        DIAG_AG -->|7b. Fetch Data| SENS
        SENS -->|Readings| DIAG_AG
        
        GEN_AG -->|7c. Direct Prompt| LLM
    end
    
    %% Convergence
    RAG_AG -->|8. Generate Response| LLM
    DIAG_AG -->|8. Generate Response| LLM
    
    LLM -->|9. Generated Text| MEM_OUT
    MEM_OUT -->|10. Final Response| API
    API -->|JSON| UI
    UI -->|Display| User
    
    %% Styling
    style User fill:#f9f,stroke:#333
    style UI fill:#aff,stroke:#333
    style ORC fill:#faa,stroke:#333
    style DB fill:#eee,stroke:#333
```

---


---

## Data Lifecycle: Generation, Storage & Retrieval

This diagram details **where** data comes from, **how** it is processed, and **where** it is persistently or temporarily stored.

### Key Data Flows
1.  **Vector Data (Long-term)**: Documents are ingested → Chunked → Embedded → Stored in ChromaDB.
2.  **Session Data (Short-term)**: Chat messages are stored in MemoryService RAM during the conversation.
3.  **Sensor Data (Real-time)**: Generated mathematically by the Simulator on-the-fly (not stored).
4.  **Retrieval**: The RAG Agent vectors user queries to "pull" relevant context from ChromaDB.

```mermaid
flowchart TD
    %% Subgraphs for Logical Grouping
    subgraph Sources [Data Generation Sources]
        Docs[Markdown Documents\n(SOPs, Manuals)]
        UserInput[User Chat Message]
        Sim[Sensor Simulator\n(Math Functions)]
        CSV[CSV Log File]
    end

    subgraph Processing [Processing & Logic]
        Split[Text Splitter]
        Embed[Embedding Model\n(HuggingFace)]
        LLM_Proc[LLM Inference]
        Pandas[Pandas Analysis]
    end

    subgraph Storage [Storage Systems]
        VDB[(ChromaDB\nVector Store)]
        RAM[Memory Service\n(RAM / Session State)]
        State[Simulator State\n(RAM)]
    end

    %% ==========================================
    %% 1. KNOWLEDGE INGESTION (Write to Vector DB)
    %% ==========================================
    Docs -->|1. Load & Chunk| Split
    Split -->|2. Text Chunks| Embed
    Embed -->|3. Generate Vectors| VDB
    style VDB fill:#faa,stroke:#333  %% Highlight Storage

    %% ==========================================
    %% 2. RAG RETRIEVAL (Read from Vector DB)
    %% ==========================================
    UserInput -->|4. Query| Embed
    Embed -.->|5. Vector Search| VDB
    VDB -.->|6. Retrieve Similar Docs| LLM_Proc
    
    %% ==========================================
    %% 3. CHAT MEMORY (Write/Read Session)
    %% ==========================================
    UserInput -->|7. Store Msg| RAM
    RAM -.->|8. Retrieve History| LLM_Proc
    LLM_Proc -->|9. Generate Answer| RAM
    
    %% ==========================================
    %% 4. REAL-TIME SENSORS (Transient Generation)
    %% ==========================================
    Sim -->|10. Generate Values\n(Temp, Vib, RPM)| State
    State -.->|11. Read Current State| LLM_Proc
    
    %% ==========================================
    %% 5. LOG ANALYSIS (File Processing)
    %% ==========================================
    CSV -->|12. Upload| Pandas
    Pandas -->|13. Statistical Summary| LLM_Proc

    %% Output
    LLM_Proc -->|14. Final Response| UserOutput([Frontend UI])

    %% Styling
    linkStyle 0,1,2 stroke:green,stroke-width:2px; %% Ingestion Flow
    linkStyle 4,5 stroke:blue,stroke-width:2px;    %% Retrieval Flow
```

---

## File-by-File Reference

### Backend Entry Point

#### `backend/app/main.py`

The FastAPI application entry point. Initializes the server and registers all API routers.

| Function | Parameters | Returns | Description |
|----------|------------|---------|-------------|
| `read_root()` | None | `{"message": "System Operational"}` | Health check endpoint at `/` |

**Global Setup:**
- Creates `FastAPI` instance with title "Smart Manufacturing Assistant"
- Registers `sensors.router` for `/sensors` and `/fault` endpoints
- Registers `chat.router` for `/chat` and `/chat/*` endpoints
- Registers `maintenance.router` for `/maintenance/*` endpoints
- Starts Uvicorn server on port 8090

---

### Core Module

#### `backend/app/core/orchestrator.py`

The central coordinator for all AI interactions. Routes queries to appropriate agents and manages the request lifecycle.

| Class | Description |
|-------|-------------|
| `Orchestrator` | Main coordinator class that handles request processing |

| Method | Parameters | Returns | Description |
|--------|------------|---------|-------------|
| `__init__()` | None | None | Initializes with system prompt for query routing |
| `route_query(user_query, session_id)` | `str`, `str` | `dict` | Uses LLM to classify query into RAG/DIAGNOSTICS/GENERAL |
| `handle_request(user_query, session_id)` | `str`, `str` | `str` | Main entry point: validates, routes, processes, returns response |

**Request Flow in `handle_request()`:**
1. Validate input with GuardrailService
2. Save user message to MemoryService
3. Route query to appropriate agent
4. Execute agent logic (RAG retrieval, sensor analysis, or general chat)
5. Save AI response to MemoryService
6. Return response

---

### Services

#### `backend/app/services/llm_service.py`

Interface to the Ollama/Mistral local LLM server.

| Class | Description |
|-------|-------------|
| `LLMService` | HTTP client for Ollama API |

| Method | Parameters | Returns | Description |
|--------|------------|---------|-------------|
| `__init__(model, base_url)` | `str`, `str` | None | Initialize with model name and Ollama URL |
| `generate(prompt)` | `str` | `str` | Single-turn text generation (completion style) |
| `chat(messages)` | `list` | `str` | Multi-turn conversation (chat style) |

**Configuration:**
- Default model: `"mistral"`
- Default URL: `"http://localhost:11434"`

---

#### `backend/app/services/rag_service.py`

Document retrieval using ChromaDB vector database.

| Class | Description |
|-------|-------------|
| `RAGService` | Manages document ingestion and semantic search |

| Method | Parameters | Returns | Description |
|--------|------------|---------|-------------|
| `__init__(data_path)` | `str` | None | Initialize ChromaDB, ingest documents if new |
| `ingest_data()` | None | None | Load .md files, split by headers, store embeddings |
| `query(question, k)` | `str`, `int` | `List[Document]` | Retrieve k most similar documents |

**Storage:**
- Persist directory: `backend/app/data/chroma_db`
- Embedding model: HuggingFace `all-MiniLM-L6-v2`

---

#### `backend/app/services/memory_service.py`

Session-based chat history management using LangChain.

| Class | Description |
|-------|-------------|
| `MemoryService` | Manages conversation history per session |

| Method | Parameters | Returns | Description |
|--------|------------|---------|-------------|
| `__init__()` | None | None | Initialize empty sessions dictionary |
| `get_session_history(session_id)` | `str` | `ChatMessageHistory` | Get or create history for session |
| `add_user_message(session_id, message)` | `str`, `str` | None | Add user message to history |
| `add_ai_message(session_id, message)` | `str`, `str` | None | Add AI message to history |
| `get_formatted_history(session_id)` | `str` | `str` | Format history as "User: ...\nAI: ..." |
| `clear_history(session_id)` | `str` | None | Clear all messages in session |
| `get_all_sessions()` | None | `List[str]` | List all session IDs |
| `get_messages(session_id)` | `str` | `List[Dict]` | Get messages as list of dicts |

---

#### `backend/app/services/guardrail_service.py`

Safety and relevance filtering for user inputs.

| Class | Description |
|-------|-------------|
| `GuardrailService` | Validates inputs for safety and topic relevance |

| Method | Parameters | Returns | Description |
|--------|------------|---------|-------------|
| `__init__()` | None | None | Initialize forbidden topics list |
| `check_relevance(text)` | `str` | `bool` | Use LLM to verify manufacturing relevance |
| `validate_input(text)` | `str` | `Tuple[bool, str]` | Check blocklist + relevance, return (valid, reason) |
| `validate_output(text)` | `str` | `Tuple[bool, str]` | Validate AI output (placeholder) |

**Blocked Topics:**
- politics, religion, finance, medical advice
- vote, election, bomb, weapon, kill, suicide
- stock market, investment

---

#### `backend/app/services/inventory_service.py`

Spare parts inventory management.

| Class | Description |
|-------|-------------|
| `InventoryService` | Manages spare parts data and alerts |

| Method | Parameters | Returns | Description |
|--------|------------|---------|-------------|
| `__init__()` | None | None | Initialize mock inventory data |
| `get_inventory()` | None | `List[Dict]` | Return all spare parts |
| `trigger_scarcity_alert(part_name, machine_id)` | `str`, `str` | `dict` | Simulate alert to management |

---

#### `backend/app/services/simulator.py`

Machine sensor data simulation.

| Class | Description |
|-------|-------------|
| `SensorSimulator` | Generates realistic sensor readings |

| Method | Parameters | Returns | Description |
|--------|------------|---------|-------------|
| `__init__()` | None | None | Initialize machines with nominal values |
| `get_readings()` | None | `Dict[str, Dict]` | Get current sensor data with fluctuations |
| `trigger_fault(machine_id, fault_type)` | `str`, `str` | `dict` | Inject fault condition for testing |

**Simulated Machines:**
- CNC-204, PRESS-505, ROBOT-101

**Fault Types:**
- `overheat`: Temperature → 110°C
- `vibration`: Vibration → 2.5 mm/s
- `pressure_loss`: Pressure → 20 PSI

---

### API Layer

#### `backend/app/api/chat.py`

Chat and session management endpoints.

| Endpoint | Method | Parameters | Returns | Description |
|----------|--------|------------|---------|-------------|
| `/chat` | POST | `{message, session_id}` | `{response}` | Send message, get AI response |
| `/chat/sessions` | GET | None | `{sessions: [...]}` | List all session IDs |
| `/chat/history/{session_id}` | GET | `session_id` | `{history: [...]}` | Get session messages |
| `/chat/history/{session_id}` | DELETE | `session_id` | `{status, message}` | Clear session |

---

#### `backend/app/api/sensors.py`

Sensor data and fault injection endpoints.

| Endpoint | Method | Parameters | Returns | Description |
|----------|--------|------------|---------|-------------|
| `/sensors` | GET | None | `{machine: {sensors...}}` | Get all sensor readings |
| `/fault` | POST | `{machine_id, fault_type}` | `{message, state}` | Trigger fault |

---

#### `backend/app/api/maintenance.py`

Inventory and log analysis endpoints.

| Endpoint | Method | Parameters | Returns | Description |
|----------|--------|------------|---------|-------------|
| `/maintenance/inventory` | GET | None | `{inventory: [...]}` | Get parts list |
| `/maintenance/alert` | POST | `{part_name, machine_id}` | `{status, message}` | Send alert |
| `/maintenance/analyze-log` | POST | `file (CSV)` | `{stats, report}` | Analyze log file |

---

### Frontend

#### `frontend/app.py`

Streamlit application entry point. Configures page layout and navigation.

#### `frontend/utils/api_client.py`

HTTP client functions for backend communication.

| Function | Parameters | Returns | Description |
|----------|------------|---------|-------------|
| `get_sensor_data()` | None | `dict` | Fetch sensor readings |
| `send_chat_message(message, session_id)` | `str`, `str` | `str` | Send chat, get response |
| `trigger_fault(machine_id, fault_type)` | `str`, `str` | `dict` | Trigger machine fault |
| `get_chat_sessions()` | None | `List[str]` | Get all sessions |
| `get_chat_history(session_id)` | `str` | `List[Dict]` | Get session history |
| `delete_chat_history(session_id)` | `str` | `bool` | Clear session |
| `get_inventory()` | None | `List[Dict]` | Get spare parts |
| `trigger_scarcity_alert(machine_id, part_name)` | `str`, `str` | `bool` | Send alert |
| `analyze_log(file_bytes)` | `bytes` | `dict` | Analyze CSV |

#### `frontend/pages/chat.py`

Chat interface with session management, history viewer, and clear history functionality.

#### `frontend/pages/dashboard.py`

Sensor monitoring dashboard with real-time updates and fault injection controls.

#### `frontend/pages/maintenance.py`

Two-tab interface:
- **Tab 1**: Spare parts inventory with scarcity alert buttons
- **Tab 2**: CSV log upload with visualization and AI analysis

---

## API Reference

### Quick Reference Table

| Endpoint | Method | Description |
|----------|--------|-------------|
| `GET /` | GET | Health check |
| `GET /sensors` | GET | Get sensor data |
| `POST /fault` | POST | Trigger fault |
| `POST /chat` | POST | Send chat message |
| `GET /chat/sessions` | GET | List sessions |
| `GET /chat/history/{id}` | GET | Get history |
| `DELETE /chat/history/{id}` | DELETE | Clear history |
| `GET /maintenance/inventory` | GET | Get parts |
| `POST /maintenance/alert` | POST | Send alert |
| `POST /maintenance/analyze-log` | POST | Analyze CSV |

---

## Final Walkthrough

### How the System Works End-to-End

#### Example 1: User Asks About Machine Maintenance

```
User: "How do I maintain the hydraulic pump?"

1. [Frontend] User types message in Chat UI
2. [api_client.py] send_chat_message() sends POST to /chat
3. [chat.py] Receives request, calls orchestrator.handle_request()
4. [orchestrator.py] 
   a. guardrail_service.validate_input() → PASS (manufacturing topic)
   b. memory_service.add_user_message() → Saves to session
   c. route_query() → LLM classifies as "RAG" (needs documentation)
   d. rag_service.query() → ChromaDB finds relevant SOP sections
   e. LLM generates answer using retrieved documents
   f. memory_service.add_ai_message() → Saves response
5. [chat.py] Returns {"response": "To maintain the hydraulic pump..."}
6. [Frontend] Displays AI response in chat
```

#### Example 2: User Uploads a Log File

```
User: Uploads machine_log.csv

1. [Frontend] User selects file in Maintenance → Log Analysis tab
2. [maintenance.py] Streamlit shows preview and charts
3. User clicks "Analyze with AI"
4. [api_client.py] analyze_log() sends file to /maintenance/analyze-log
5. [maintenance.py API]
   a. Pandas reads CSV into DataFrame
   b. df.describe() generates statistics
   c. LLM receives stats and generates performance report
6. [Frontend] Displays AI report and expandable stats
```

#### Example 3: Guardrail Blocks Off-Topic Query

```
User: "Who should I vote for?"

1. [Frontend] User types message
2. [orchestrator.py] 
   a. guardrail_service.validate_input()
   b. Keyword "vote" found in forbidden_topics
   c. Returns: (False, "I cannot discuss vote as it is outside...")
3. [chat.py] Returns the rejection message
4. [Frontend] Displays: "I cannot discuss vote as it is outside the scope of manufacturing support."
```

### Running the Application

```bash
# Terminal 1: Start Ollama
ollama run mistral

# Terminal 2: Start Backend
cd backend
python -m app.main
# Server runs at http://localhost:8090

# Terminal 3: Start Frontend  
cd frontend
streamlit run app.py
# UI available at http://localhost:8501
```

### Testing the Features

1. **Chat**: Navigate to Chat page, ask "What sensors are on Machine 1?"
2. **Diagnostics**: Ask "Is there any fault in the machines right now?"
3. **RAG**: Ask "How do I calibrate the pressure sensor?"
4. **Guardrails**: Ask "What's the weather today?" (should be blocked)
5. **Inventory**: Go to Maintenance → Spare Parts, click "Report Scarcity"
6. **Log Analysis**: Upload `dummy_log.csv`, click "Analyze with AI"

---

## Summary

The Smart Manufacturing Assistant is a complete AI-powered solution for manufacturing plant operations. It combines:

- **Local AI** (Ollama/Mistral) for privacy and cost efficiency
- **Vector Search** (ChromaDB) for intelligent document retrieval
- **Multi-Agent Routing** for specialized handling of different query types
- **Safety Guardrails** for appropriate and focused responses
- **Session Memory** for context-aware conversations
- **Real-time Monitoring** for sensor data visualization
- **Predictive Maintenance** for log analysis and inventory management
