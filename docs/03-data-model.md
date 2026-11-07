# Data Model

## Modeling approach

Separate source facts, canonical entities, case facts, and temporal versions.

## Core entities

| Entity | Purpose | Important fields |
|---|---|---|
| `ExcursionEvent` | Temperature excursion alert | `event_id`, `alert_ts_utc`, `excursion_start_utc`, `product_ref_as_received`, `raw_payload` |
| `Case` | Adjudication unit | `case_id`, `state`, `opened_at`, `reopen_count` |
| `CaseEvent` | Immutable workflow history | `event_id`, `case_id`, `event_type`, `occurred_at`, `actor`, `payload` |
| `Product` | Canonical product | `product_id`, `canonical_name`, `presentation` |
| `ProductAlias` | Alternative identifiers | `alias_value`, `canonical_product_id`, `confidence`, `source` |
| `Facility` | Canonical physical site | `facility_id`, `canonical_name`, `timezone` |
| `Specification` | Versioned storage requirement | `product_id`, `storage_condition`, `effective_from`, `effective_to` |
| `SOPRevision` | Versioned procedure | `doc_id`, `revision`, `effective_from`, `effective_to` |
| `StabilityStudy` | Stability evidence | `study_id`, `product_id`, `readable`, `outcome`, `permitted_excursion` |
| `EvidenceItem` | Case-linked evidence | `evidence_id`, `case_id`, `source_system`, `retrieved_at`, `content_hash` |
| `Recommendation` | Draft disposition and rationale | `case_id`, `rules_version`, `model_version`, `prompt_version`, `proposed_disposition` |
| `Disposition` | Human-approved outcome | `case_id`, `decision`, `decided_by`, `decided_at`, `override_reason` |
| `Notification` | Regulatory notification record | `case_id`, `due_at`, `submitted_at`, `status` |

## Time-based queries

The system must answer: *“What storage specification applied to this product on 12 May 2026?”* and *“Which SOP revision governed this facility at the time of the excursion?”*

```sql
SELECT *
FROM product_specification
WHERE product_id = :product_id
  AND effective_from <= :as_at_date
  AND (effective_to IS NULL OR effective_to > :as_at_date)
ORDER BY effective_from DESC
LIMIT 1;
```

## Time rules

- System timestamps are UTC.
- Reviewer activity retains original local timestamp and UTC equivalent.
- Facility timezone corrections are versioned.
- `alert_ts_utc` drives the regulatory clock.
- Document and specification lookups use case-relevant date.
- Corrections create new versions; historical records retain original references.

## Case reopening

A reopened case is a new adjudication attempt linked to the same underlying event, preserving original evidence, recommendation, decision, and override reason.
