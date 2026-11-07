# Data Flow

```mermaid
flowchart LR
    Workbook[Workbook Extract] --> Loader[Workbook Loader] --> Normalizer --> Resolver[Identity Resolver]
    Resolver --> Temporal[Temporal Service] --> CaseService
    CaseService --> Clock[Regulatory Clock] --> Rules --> LLM[LLM Stub] --> Report[Reports]
```
