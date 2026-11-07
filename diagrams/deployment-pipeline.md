# Deployment Pipeline

```mermaid
flowchart LR
    Commit --> CI[CI Tests] --> Staging --> Eval[Evaluation] --> Approval --> Canary --> Production
    Production --> Monitor --> Rollback
```
