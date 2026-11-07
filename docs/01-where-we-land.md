# Where We Land

## Position

KCCS should build an **adjudication control plane**, not another isolated rules engine or a general-purpose AI assistant. The platform should make excursion cases traceable, time-correct, evidence-linked, and reviewable, while using AI to prepare and explain decisions rather than silently make regulated dispositions.

## Requirements and traceability

| Requirement | Attribute | Brief/pack evidence | Design consequence |
|---|---|---|---|
| Preserve the regulatory notification clock | Time correctness, auditability | `reg_window_hours` and `hours_to_notification` run from `alert_ts_utc`; `days_to_disposition` is separate | Store immutable alert time and calculate clock state from event time |
| Support incomplete and inconsistent master data | Data quality, resolution | Product references may be brand names, SKUs, GTINs, or blank; facility records duplicate physical sites | Maintain source values alongside canonical resolved entities and confidence/provenance metadata |
| Preserve evidence available at decision time | Temporal correctness | `spec_text_as_received` may differ from the current product master | Store effective-dated snapshots and resolve references as-at the relevant case date |
| Support human accountability | Auditability, explainability | Reviewers override recommendations; many overrides have no recorded reason | Capture recommendation, inputs, evidence, decision, actor, reason, and timestamp immutably |
| Avoid unsafe automation | Safety, compliance | Rules-engine recommendation column now contains assistant drafts; stability index is incomplete | Treat AI output as decision support; require explicit human approval for regulated dispositions |
| Operate across heterogeneous systems | Integration, resilience | Nine systems with different access methods and known defects | Use adapters, normalization, reconciliation, and failure isolation |
| Handle real operational delays | Workflow, observability | Review queue waits and late dispositions are normal | Model waits, reminders, escalations, and clock-breach risk explicitly |
| Support re-adjudication | History, correctness | 61 cases were re-adjudicated under bulletin TT-CB-114 | Version cases and create a new adjudication attempt linked to the same event |

## Deliberately not building

- A fully autonomous disposition engine.
- A complete enterprise MDM platform.
- A replacement for ERP, LIMS, document management, or Sentinel.
- A generic document-understanding product.
- Automatic regulatory filing.

## Phased rollout

| Phase | Duration | Scope | Outcome |
|---|---:|---|---|
| Phase 0 — Foundations | 4–6 weeks | Canonical data model, ingestion, temporal resolution, audit log, prototype | Reliable case timeline and evidence linkage |
| Phase 1 — Pilot | 6–8 weeks | One tenant, reviewer workbench, notification clock, override capture | Reduced manual evidence gathering without changing accountability |
| Phase 2 — Controlled production | 8–12 weeks | Rules plus assistant recommendations, evidence extraction, monitoring, rollback | Measurable queue-time and quality improvement |
| Phase 3 — Scale | Ongoing | More tenants, adapters, stability coverage, closed-loop learning | Platform reuse and improved consistency |

## Ambiguities and positions

| Ambiguity | Position |
|---|---|
| What happens when a stability study cannot be read? | Treat it as an evidence gap, not automatically as compliance failure |
| Which timestamp governs the regulatory clock? | The alert timestamp |
| Can an AI recommendation become a disposition? | No; it requires reviewer approval |
| Should historical data be corrected in place? | No; correct forward-looking records and preserve original source values |
| What if source systems disagree? | Preserve both values, expose conflict, and never silently overwrite evidence |

## Board items to challenge

1. **“Use AI to automate adjudication end to end.”** Too strong. The correct objective is human-in-the-loop adjudication with measurable reduction in preparation and review time.
2. **“Fix the data first, then build the system.”** Build temporal, provenance-aware ingestion now and make uncertainty visible.
3. **“A single canonical product master will solve identity.”** Aliases, presentation differences, and stale references still require resolution and auditability.
4. **“Measure success only by reduced reviewer time.”** Also measure evidence completeness, notification timeliness, consistency, auditability, and rework.
