# AI-Data-Agent-Project
A sophisticated multi-agent system for intelligent data processing and analysis using LangGraph. This project demonstrates a complete implementation of an agentic architecture with specialised sub-agents for SQL operations and ETL workflows.


---

## Overview

**Agentic AI Data Agent** is an intelligent system that processes natural language queries and routes them to specialised agents for execution. The main agent serves as an intelligent router that understands user intent and delegates tasks to either the **SQL Analyst Agent** (for database queries) or the **ETL Analyst Agent** (for data extraction and transformation).

This project showcases modern AI engineering practices including:
- Multi-agent orchestration with LangGraph
- Intelligent routing based on natural language understanding
- Safety validation for SQL queries
- Tool-based agent architecture
- Dynamic LLM selection based on task complexity

---- 

## What Problem This Solves

Most teams have people who need answers from company data — sales trends, user counts, ride completion rates — but don't know SQL, and don't want to wait on a data analyst for every ad-hoc question. At the same time, raw "text-to-SQL" tools are risky: an LLM that can write SQL can also write a `DELETE FROM users;` if the prompt is even slightly ambiguous or adversarial.

This project builds a multi-agent system that lets a non-technical user ask a plain-English question and get back a safe, accurate answer grounded in the actual database schema — without ever exposing a raw, unvalidated SQL execution path. It also extends beyond querying: to handle the data engineering side (loading and transforming data), not just reading it.

### What the Router Does

The **Data Agent (Router)** is the single entry point for every user request. Its job is to classify intent and delegate — it doesn't generate SQL, transform data, or talk to the database itself.

When a request comes in, the router decides: *is this a question about existing data (read/analyze), or is this a request to move/transform data (extract, load, pipeline work)?* Based on that classification, it hands the request off to the appropriate specialist — the SQL Analyst Agent or the ETL Analyst Agent — and returns whatever that sub-agent produces.

This keeps the system modular: the router only needs to reason about *intent*, and each sub-agent only needs to be excellent at its own narrow job. New capabilities (e.g., a future "Reporting Agent") plug in by adding another branch at the router, without touching the internals of the existing agents.

### Why Separate SQL vs ETL Agents (Instead of One Agent Doing Both)

These are fundamentally different jobs with different risk profiles, different inputs, and different failure modes — collapsing them into one agent would mean sacrificing safety, clarity, or both:

- **Different goals.** The SQL Analyst Agent answers questions about data that already exists. The ETL Analyst Agent moves and reshapes data into the system in the first place. One is read-only by design; the other is inherently write-heavy. Merging them muddies that boundary — a "smart" agent that both answers questions *and* writes data is much harder to reason about and secure.

- **Different safety requirements.** The SQL Analyst Agent has a strict Safety Validation step that rejects any query attempting to modify the database — this only makes sense because the agent's entire job is supposed to be read-only. The ETL Agent, by contrast, is *expected* to write data (Extract, Load, Transform) as its core function. A single merged agent would need to distinguish "this write is my job" from "this write is a rejected exploit" using the same guardrail — a much fuzzier and riskier line to draw than just keeping the two agents separate from the start.

- **Different internal pipelines.** SQL Analyst follows a linear "understand → generate → validate → execute → explain" flow tailored to answering questions. ETL Analyst follows a distinct "extract → transform → load" pipeline suited to batch/data-movement logic and code execution rather than natural-language answer generation. Trying to encode both pipelines as conditional branches in a single agent would make the graph harder to test, extend, and explain — whereas two focused agents each remain simple enough to reason about, debug, and extend independently.


------- 

## Architecture

The system follows a hierarchical agent architecture:

```
┌─────────────────────────────────────────────────────────────┐
│                    Data Agent (Router)                      │
│         Routes user queries to appropriate sub-agents       │
└────────────────────┬────────────────────────────────────────┘
                     │
         ┌───────────┴───────────┐
         │                       │
         ▼                       ▼
    ┌──────────────┐        ┌──────────────┐
    │ SQL Analyst  │        │ ETL Analyst  │
    │   Agent      │        │   Agent      │
    └──────────────┘        └──────────────┘
         │                       │
         ├─► Query Curation      ├─► Extract Load
         ├─► Schema Context      ├─► Transform Load
         ├─► SQL Generation      └─► Code Execution
         ├─► Safety Validation   
         ├─► Query Execution     
         └─► Answer Generation   
```

<img width="874" height="358" alt="Screenshot 2026-09-07 at 9 42 46 PM" src="https://github.com/user-attachments/assets/1789907c-7b3d-46c3-b480-6272fc144b66" />


<img width="857" height="714" alt="ETL AI Agent Flow-diagram" src="https://github.com/user-attachments/assets/116f19d6-0423-4004-ae5e-4bd46011aef3" />


### State Flow

1. **User Input** → Natural language query
2. **Router Node** → Classifies query as SQL or ETL
3. **Agent Dispatch** → Routes to appropriate sub-agent
4. **Processing** → Each agent processes the task
5. **Output** → Returns structured result to user

---

## Features

### Core Capabilities

- **Intelligent Query Routing**: Automatically classifies user queries as SQL or ETL operations
- **SQL Analysis Agent**:
  - Natural language to SQL query conversion
  - Automatic schema context gathering
  - SQL safety validation (prevents harmful operations)
  - Query execution on PostgreSQL database
  - Intelligent query refinement

- **ETL Agent**:
  - API data extraction (JSON to structured formats)
  - Data transformation using Pandas
  - Multi-format support (CSV, JSON, Parquet)
  - Dynamic code generation based on user requirements
  - Safe code execution

- **Multi-LLM Support**:
  - Low-complexity queries: Faster, cost-effective LLM
  - Medium-complexity queries: Balanced LLM
  - High-complexity queries: Premium LLM (Claude)

- **Safety & Validation**:
  - SQL query safety checking
  - Protection against database modifications (INSERT, UPDATE, DELETE, DROP, etc.)
  - Input validation and sanitisation
  - Structured output validation using Pydantic

---

## Prerequisites

- Python 3.12+
- PostgreSQL database (for SQL operations)
- API keys for LLM providers (Claude and/or OpenAI)
- Virtual environment (recommended)

---

## Project Structure

```
Data_Agent/
├── agents/                          # Agent implementations
│   ├── __init__.py
│   ├── data_agent.py               # Main router agent
│   ├── sql_analyst.py              # SQL query agent
│   └── etl_analyst.py              # ETL operations agent
│
├── Models/                          # Data models
│   ├── __init__.py
│   └── schema.py                   # Pydantic schemas for state management
│
├── utils/                           # Utility modules
│   ├── __init__.py
│   ├── database.py                 # PostgreSQL utilities
│   ├── etl_tools.py                # ETL operations toolkit
│   ├── llm_pick.py                 # LLM selection logic
│
├── data/                            # Data directory
│   ├── extract/                     # Extracted data storage
│   ├── transform/                   # Transformed data storage
│   ├── payments.csv                 # Sample dataset
│   ├── ratings.csv                  # Sample dataset
│   ├── rides.csv                    # Sample dataset
│   ├── users.csv                    # Sample dataset
│   └── vehicles.csv                 # Sample dataset
│
├── main.py                          # Entry point
├── feed_db.py                       # Database initialization script
├── pyproject.toml                   # Project metadata and dependencies
└── README.md                         # This file
```

---

## Agent Descriptions

### 1. **Data Agent (Main Router)**
**File:** `agents/data_agent.py`

**Responsibility:** 
- Receives natural language user queries
- Classifies queries as either SQL or ETL operations
- Routes queries to appropriate sub-agents
- Aggregates results and returns to user

**Components:**
- **Router Node**: Uses structured output to classify query intent
- **Conditional Routing**: Routes to SQL or ETL based on classification
- **Graph Orchestration**: Manages workflow using LangGraph

---

### 2. **SQL Analyst Agent**
**File:** `agents/sql_analyst.py`

**Responsibility:**
- Converts natural language queries to SQL
- Handles all database query operations
- Validates query safety
- Executes queries and returns results

**Workflow:**
1. **Query Curation** - Refines user question for clarity
2. **Context Gathering** - Fetches database schema details
3. **Prompt Construction** - Creates detailed context for LLM
4. **SQL Generation** - Generates SQL query using LLM
5. **Safety Check** - Validates query safety
6. **Query Execution** - Executes validated query on database
7. **Answer Generation** - Formats and returns results

**Safety Features:**
- Prevents execution of dangerous commands (INSERT, UPDATE, DELETE, DROP, ALTER)
- Validates query before execution
- Automatic result limiting to 10 rows (unless specified)
- Schema validation against the database

---

### 3. **ETL Analyst Agent**
**File:** `agents/etl_analyst.py`

**Responsibility:**
- Handles data extraction from APIs
- Performs data transformation using Pandas
- Manages data loading to various formats
- Executes code safely in a controlled environment

**Workflow:**
1. **Tool Binding** - Attaches ETL tools to LLM
2. **User Intent Understanding** - Analyzes transformation requirements
3. **Tool Selection** - Chooses appropriate ETL operation
4. **Code Generation** - Generates Pandas code for transformation
5. **Safe Execution** - Executes generated code in sandboxed environment
6. **Result Reporting** - Returns execution status and generated code

**Supported Tools:**
- **extract_load_tool**: Extract from API → Load to storage
- **transform_load_tool**: Transform data using Pandas → Load result

**Supported Formats:**
- CSV (default)
- JSON (Lines or Records)
- Parquet

---

## Examples

### Example 1: Database Query

**User Query:**
```
"Find the top 5 customers who have spent the most money on orders in the last year, and provide their names and total spending amounts."
```

**Processing:**
1. Router classifies as a SQL query
2. SQL Agent fetches schema
3. Generates: `SELECT vehicle_type, AVG(rating) FROM rides GROUP BY vehicle_type LIMIT 10`
4. Validates safety ✓
5. Executes and returns results

**Output Sample** 
<img width="1026" height="513" alt="output_sample" src="https://github.com/user-attachments/assets/0f4a9c74-f5af-4fb9-953b-6ddf18c936d8" />


---

### Example 2: Data Extraction

**User Query:**
```
"Extract the data from 'https://pokeapi.co/api/v2/pokemon' and save it as CSV"
```

**Processing:**
1. Router classifies as an ETL operation
2. ETL Agent selects extract_load_tool
3. Makes API request to endpoint
4. Normalizes JSON response
5. Saves to `data/extract/extracted_data.csv`

---

### Example 3: Data Transformation

**User Query:**
```
"Transform rides.csv to filter only rides with rating > 4.0 and save as JSON"
```

**Processing:**
1. Router classifies it as an ETL operation
2. ETL Agent analyses the requirement
3. Generates Pandas code to filter and transform
4. Executes code safely
5. Saves result to `data/transform/` in JSON format

---

## Security Features

✅ **SQL Safety Validation**
- Query inspection before execution
- Blocks destructive operations
- Database structure protection

✅ **Safe Code Execution**
- Sandboxed Python code execution
- Input validation
- Error handling and reporting

✅ **Environment Security**
- Credentials stored in `.env` (not in code)
- Sensitive data protection
- Proper exception handling

---


## Environment Variables Reference

| Variable | Description | Example |
|----------|-------------|---------|
| `ANTHROPIC_API_KEY` | Claude API key | `sk-ant-...` |
| `OPENAI_API_KEY` | OpenAI API key | `sk-...` |
| `host` | PostgreSQL host | `localhost` |
| `port` | PostgreSQL port | `5432` |
| `user` | PostgreSQL user | `postgres` |
| `password` | PostgreSQL password | `your_password` |
| `database` | Database name | `data_agent_db` |

---

## Troubleshooting

**Issue:** "Database connection failed"  
**Solution:** Verify PostgreSQL is running and credentials in `.env` are correct

**Issue:** "API key not found"  
**Solution:** Ensure API keys are set in the `.env` file

**Issue:** "SQL query unsafe"  
**Solution:** The query contains destructive operations. Reformulate as a SELECT query only

**Issue:** "Module not found"  
**Solution:** Activate the virtual environment and reinstall dependencies

---

## Performance Considerations

- **Query Complexity**: Low-complexity queries use faster LLMs
- **Database Optimization**: Add indexes for frequently queried columns
- **API Rate Limiting**: Respect rate limits of external APIs
- **Memory Usage**: Large dataset transformations may require optimization


## License

This project is part of an AI engineering demonstration.

---

## Learning Resources

- [LangGraph Documentation](https://langchain-ai.github.io/langgraph/)
- [LangChain Documentation](https://python.langchain.com/)
- [Claude API Reference](https://docs.anthropic.com/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)

---

**Last Updated:** September 2026
**Version:** 0.1.0
