# 🚨 Threat Intel RAG Pipeline  

Graph-based **Retrieval-Augmented Generation (RAG)** system for **AI-powered threat intelligence**.  
All data — documents, text chunks, embeddings (via Neo4j native vector indexes), indicators, campaigns, etc. — are stored directly in **Neo4j**.  

---

## ✨ Features  

- ⚡ **Neo4j-only backend**  
  Stores documents, text chunks, embeddings, indicators, and campaigns → super fast queries.  
- 📄 **PDF ingestion pipeline**  
- 🎯 **Campaign support**  
  - Auto-created from PDF filenames  
- 🌐 **FastAPI REST API**  
  - Endpoints: `search`, `context`, `timeline`, `clusters`, `campaign`  
- 💬 **Chatbot (NiceGUI)**  
  - Frontend UI built with NiceGUI  
  - Connects to FastAPI agent routes  
  - Generates conclusions using **Meta-LLaMA** over retrieved chunks  

---

## 🏗️ Architecture  

1. **Pipeline**  
   PDFs → chunked → embeddings generated → inserted into Neo4j with indicators + campaign links  

2. **Graph Database (Neo4j)**  
   - **Nodes:** `Document`, `Chunk`, `Indicator`, `Campaign`  
   - **Relationships:** `PART_OF`, `MENTIONED_IN`, `PART_OF_CAMPAIGN`  

3. **FastAPI**  
   - REST API + LangGraph Agent  

4. **Chatbot UI**  
   - Built with NiceGUI  
   - Calls FastAPI routes  
   - Meta-LLaMA generates final conclusions  

---

## 🔗 System Diagram  

```mermaid
flowchart TD
    A[PDFs] --> B[Pipeline: Ingest → Chunk → Embed → Indicators + Campaign Links]
    B --> C[(Neo4j Graph Database)]

    %% Neo4j storage
    C -->|Stores| D[Document]
    C -->|Stores| E[Chunk]
    C -->|Stores| F[Indicator]
    C -->|Stores| G[Campaign]

    %% Relationships
    D -->|PART_OF| E
    F -->|MENTIONED_IN| D
    D -->|PART_OF_CAMPAIGN| G

    %% API Layer
    C --> H[FastAPI: REST + LangGraph Agent]
    H --> |query|C

    %% Chatbot UI
    H --> I[Meta-LLaMA Model: Conclusion Generator]
    I --> J[NiceGUI Chatbot UI]
    J --> |query| H
```

## 🛠️ Tech Stack

| Component     | Role                           |
| ------------- | ------------------------------ |
| **Python**    | Pipeline + API                 |
| **NiceGUI**   | Frontend chatbot               |
| **FastAPI**   | REST backend                   |
| **Neo4j**     | Graph database + vector search |
| **LangChain** | LLM orchestration & tools      |
| **Docker**    | Container orchestration        |


## ⚙️ Setup 
1. Clone the reo:
    ```
        git clone <>
        cd <repo>
    ```

2. Run pipeline
    ```
        make run-pipeline

        # You can run make help command and perform the required setup.
    ```

3. Run frontend
    ```
        # made as third party interface
        make run-frontend
    ```

## 🧪 Testing
For testing locally run this commmand
```
    make run-graph-container  # this runs the local neo4j vector db
    pip install -r requirements-local.txt
    make run-test
```

## 📜 API Documentation

[openapi_schema](./openapi_schema.json)
![swagger_ui](./swagger_ui.png)

## 📊 Graphs in neo4j browser 

![graph_0](./graph.png)
![!graph_1](./graph1.png)
![!graph_2](./graph2.png)
![!graph_3](./graph3.png)

## 📋 Performance Metrics

| Metric | Value |
| ------- | ------|
| Document Load Time | ~ 20s |
| Extraction & Embedding | ~20s |
| Graph Query  | < 300 ms |
| Rest API Queries | < 4200 micro seconds |


## 📌 Deliverables Checklist
  ✅ Docker Orchestration (Neo4j, FastAPI, Nicegui, Langchain)
  ✅ Processing pipelines with unit testing
  ✅ API Endpoints (Swagger UI with documentation)
  ✅ Graph Visualization via Neo4j
  ✅ Performance Report
  ✅ README with architecture

## 📞 Info
  Developed by Tezz Chaudhary.