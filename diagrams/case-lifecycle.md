# Case Lifecycle

```mermaid
stateDiagram-v2
    [*] --> Detected
    Detected --> Triage
    Triage --> EvidenceCollection
    EvidenceCollection --> PendingReviewer
    EvidenceCollection --> EvidenceGap
    EvidenceGap --> EvidenceCollection
    PendingReviewer --> UnderReview
    UnderReview --> InformationRequest
    InformationRequest --> PendingReviewer
    UnderReview --> Dispositioned
    Dispositioned --> Reopened
    Reopened --> EvidenceCollection
    Dispositioned --> [*]
```
