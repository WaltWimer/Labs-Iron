%%{init: {'theme': 'base', 'themeVariables': { 'primaryColor': '#e1f5fe', 'edgeLabelBackground':'#ffffff', 'tertiaryColor': '#fff'}}}%%
graph LR
    %% Clear visual distribution from Left to Right (LR)

    %% --- Style Definitions ---
    classDef storage fill:#f9f9f9,stroke:#333,stroke-width:2px,rx:5,ry:5;
    classDef process fill:#e1f5fe,stroke:#0277bd,stroke-width:1px,rx:10,ry:10;
    classDef engine fill:#fff9c4,stroke:#fbc02d,stroke-width:1px,stroke-dasharray: 5 5;
    classDef tool fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px;
    classDef db fill:#e3f2fd,stroke:#1565c0,stroke-width:2px,stroke-dasharray: 5 5;

    %% --- SECTION 1: Data Origin & Ingestion (Extract & Load) ---
    subgraph S1 [1. Origin & Ingestion - Batch EL]
        direction LR
        
        Devs(20 Developers) -->|LLM Requests| Proxy[<b>Simulated Real Context:</b> Central Proxy Server<br/><i>(e.g., LiteLLM intercepting Qwen/Llama)</i>]
        
        subgraph S1_Scripts [Python Processes]
            direction TB
            ScriptGen[<b>Python Script 1:</b><br/>Generates Transactional Logs<br/><i>(Local CSV/JSON)</i>]
            
            OrchestratorEL[<b>Python Script 2: EL Orchestrator</b><br/>Uses snowflake-connector-python]
        
            ScriptGen -.->|Generates Data| DataLocal[(Local Logs<br/><i>IDs, Timestamps, Tokens,<br/>Latency, Model Used</i>)]
            OrchestratorEL ==>|Reads| DataLocal
        end
        
        Proxy -.->|Simulated Feed| ScriptGen
    end

    %% --- Ingestion Conector -> Cloud ---
    OrchestratorEL ==>|<b>Bulk Insert</b><br/>via HTTPS| RAW_LOGS

    %% --- SECTION 2: Raw Storage (Data Warehouse) ---
    subgraph S2 [2. Raw Storage - Snowflake]
        direction TB
        subgraph DB [DB: LLM_ANALYTICS_DB]
            subgraph SchemaRaw [Schema: RAW]
                RAW_LOGS[("<b>Landing Table:</b><br/>RAW_LLM_LOGS<br/><i>(Immutable Layer)</i>")]
            end
        end
    end

    %% --- SECTION 3: Transformation (Data Transformation) ---
    subgraph S3 [3. Transformation & Modeling - dbt on Snowflake]
        direction TB
        
        DBT_Tool[[<b>Tool: dbt</b><br/>Executes SQL in Snowflake]]
        
        subgraph dbt_Models [dbt Models - Business Logic]
            direction LR
            Staging[<b>Staging Layer:</b><br/>Cleaning, Casting,<br/>Standardizing & DQ Tests]
            
            subgraph Marts [Core / Marts Layer - Star Schema]
                direction TB
                Dims(dim_users<br/>dim_models<br/>dim_time)
                Fact[<b>fct_llm_generations</b><br/>Calculates:<br/>1. TPS (Hardware Perf)<br/>2. Economic Savings (Cost vs Paid)]
            end
            
            Staging ==>|Transforms & Loads| Dims
            Staging ==>|Transforms & Loads| Fact
            Dims -.->|Foreign Keys| Fact
        end
    end

    %% --- dbt Connectors ---
    RAW_LOGS ==>|Reads| DBT_Tool
    DBT_Tool ==>|Orchestrates| Staging

    %% --- SECTION 4: Analytical Consumption (BI) ---
    subgraph S4 [4. Analytical Consumption - BI]
        PBI[[<b>Power BI</b><br/>Interactive Dashboards]]
        
        Visuals(<b>Visual Goals:</b><br/>1. Volume per Developer<br/>2. Hardware Efficiency (TPS stability)<br/>3. Operational ROI)
        
        PBI --> Visuals
    end

    %% --- Final Connector ---
    Marts ==>|<b>Connectivity:</b> Import| PBI

    %% --- Style Assignment ---
    class ScriptGen,OrchestratorEL,Proxy,Staging,Fact classProcess;
    class DataLocal classStorage;
    class RAW_LOGS,Dims classDb;
    class DBT_Tool,PBI classTool;
    class Devs,Visuals classEngine;
