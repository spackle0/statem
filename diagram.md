flowchart TB
    subgraph Entry_Points
        EP[Entry Points Registry]
        NS[vigill.plugins Namespace]
        EP -->|Defines| NS
    end

    subgraph Plugin_Loading
        DM[Driver Manager]
        BP[BaseMonitor Plugin Interface]
        PC[Plugin Contract]
        CH[check() Method]
        VC[validate_config() Method]
        DM -->|Loads| BP
        BP -->|Validates| PC
        PC -->|Must Implement| CH
        PC -->|Must Implement| VC
    end

    subgraph Available_Plugins
        HTTP[HTTP Monitor]
        TCP[TCP Monitor]
        RSS[RSS Monitor]
        BP -->|Instantiates| HTTP
        BP -->|Instantiates| TCP
        BP -->|Instantiates| RSS
    end

    subgraph Monitor_Creation
        CR[Create Monitor Request]
        MT[Monitor Type]
        MI[Monitor Instance]
        CR -->|Specifies| MT
        MT -->|Passed to| DM
        DM -->|Creates Instance| MI
    end

    subgraph Execution
        SCH[Scheduler]
        SR[Status Result]
        SCH -->|Triggers| MI
        MI -->|Executes| CH
        CH -->|Returns| SR
    end

    subgraph Configuration
        PY[pyproject.toml]
        CFG[Monitor Config]
        PY -->|Registers| EP
        CFG -->|Validated by| VC
    end
