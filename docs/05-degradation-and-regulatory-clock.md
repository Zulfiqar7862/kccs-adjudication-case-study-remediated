# Degradation and Regulatory Clock

## Principle

Degradation must preserve compliance obligations, auditability, and human accountability.

## Failure modes

| Failure | Behavior | Clock impact | Action |
|---|---|---|---|
| Sentinel ingestion fails | Buffer events; alert on lag | Clock calculated when processed, but alert timestamp remains authoritative | Alert ops; replay in order |
| ERP unavailable | Use last known effective spec with staleness flag | No clock change; decision marked stale | Queue reconciliation |
| LIMS unavailable | Mark stability evidence pending | No clock change; disposition may block | Retry, alert owner |
| Document repository unavailable | Preserve metadata; retrieve later | No clock change; evidence completeness reduced | Retry retrieval |
| LLM unavailable | Fall back to deterministic rules and manual review | No clock change; no AI rationale | Rules-only path |
| Workbench unavailable | Cases remain queued | Clock continues; breach risk rises | Incident response |
| Audit log unavailable | Block disposition signing | Prevents unaccountable actions | Fail closed; restore queue |
| Clock service unavailable | Continue using persisted due timestamps | No recalculated clock | Restore and reconcile |

## Safe modes

- **Reduced mode:** ingest and store evidence; no AI recommendations; deterministic rules continue where possible.
- **Read-only mode:** preserve history and evidence; block state-changing actions.
- **Manual contingency:** QA follows existing offline process; platform records decision after restoration.

## Regulatory clock policy

The clock is not paused because an internal component is unavailable.

```text
notification_due_at = alert_ts_utc + reg_window_hours
```

If processing is delayed:

1. Preserve original `alert_ts_utc`.
2. Calculate due time from original timestamp once processed.
3. Record ingestion lag separately.
4. Raise incident when remaining time crosses threshold.
5. Never backdate or reinterpret the clock.
