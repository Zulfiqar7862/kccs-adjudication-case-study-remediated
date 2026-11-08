# Architecture: current executable and target design

## Implemented offline path
`WorkbookLoader → tenant-scoped source identity → study/SOP eligibility → separated clock assessment → advisory rules → original + linked reopen attempts → seven local exports`.

Inputs are9 relevant structured tabs of the supplied15-tab extract; all15 were read during the remediation investigation. All master product rows and negative alias observations survive loading. Invalid event identifiers/timestamps and duplicate identifiers are rejected with source-row reasons; zero usable events is an error. Metadata does not supply authoritative study tables or handwritten limits.

`CaseService` owns a dictionary of all attempts for one process. It is not a durable event-sourced service, idempotent delivery adapter or concurrency-safe workflow store. Duplicate events in a replay raise rather than silently overwrite. A crash requires rerunning from the input snapshot; deterministic identifiers support comparison, not transactional delivery guarantees. CLI file writes are ordinary filesystem writes, not atomic multi-file commit. Failures propagate to a nonzero exit. No external queue, model, database or service is contacted in this path.

## Target boundaries — NOT implemented
- Tenant-aware ingestion records receipt lag and routes notification obligations separately from noisy operational triage. Coalescing must not discard notifiable events. Fairness/deadline scheduling requires burst tests and independent monitoring.
- Versioned evidence service retrieves content-addressed study/SOP/annexure/telemetry/contract bodies with validity and knowledge dates. Human verification resolves overlaps and annotations; unavailable evidence blocks signing, not notification.
- Reviewer workbench signs regulated decisions with the tenant's required identity controls. Drafts, approvals, corrections and imported records have distinct schemas.
- Tenant/region stores and indexes enforce policy before retrieval, embeddings, caching or model use. Meridian Clause22 forbids sharing any derived model/index artefact. No shared training/cache exception is assumed.
- Retained basis store supplies seven-year full evidence and one-hour retrieval, with independently tested recovery/access controls. A mutable JSON file is not this store.

Before production, pin adapter schemas, authorization and tenancy context, delivery/idempotency keys, transaction boundaries, retry ownership, dead-letter behavior and disaster recovery objectives. Existing diagrams are conceptual target views, not evidence those integrations exist.
