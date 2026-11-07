# Validation and Test Strategy

## Correctness today

- Validate notification due time equals `alert_ts_utc + reg_window_hours`.
- Validate that a case notified within window can still have a late disposition.
- Validate reopened cases retain original history and create separate attempt.
- Validate missing/unreadable stability evidence produces evidence gap.
- Validate source and canonical values remain traceable.
- Validate every material transition produces audit event.

## Long-term reliability

- Golden-case regression tests.
- Property-based tests for clock and timezone edge cases.
- Contract tests for adapters.
- Data-quality monitoring for unresolved identities and conflicting references.
- Audit-integrity checks.
- Evaluation suites for rules, recommendations, and guardrails.
