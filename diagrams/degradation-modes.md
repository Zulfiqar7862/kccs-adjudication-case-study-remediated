# Degradation Modes

```mermaid
flowchart LR
    Normal[Normal] --> Reduced[Reduced: no LLM]
    Normal --> ReadOnly[Read-only]
    Normal --> Manual[Manual contingency]
    Reduced --> Normal
    ReadOnly --> Normal
    Manual --> Normal
```
