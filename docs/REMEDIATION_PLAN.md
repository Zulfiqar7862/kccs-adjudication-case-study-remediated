# Local remediation plan — retrospective 2026-11-08

Baseline: 1e5e19706a225616211c7efca05d89f9f7f3e09b. Local branch only. Independent review found the defects; prior passing tests did not establish workbook correctness.

## Ordered patches (red regression commit, then green implementation commit)
1. Separate notification applicability, policy, receipt evidence, assessment. No default legal window; explicit supplied window is an extracted policy, not a jurisdiction inference. Named next-business-day policies need an explicit timezone/calendar/cutoff; unspecified US state policy remains unknown.
2. Parse triage independently of authorization. Historical non-actionable labels never authorize closure; notification action remains independent.
3. Tenant-scoped multi-identifier products and study eligibility, retaining every master row and presentation uncertainty.
4. Alias candidates/conflicts/negatives/provenance; no unchecked transitive merge.
5. Tenant/document/site/as-at SOP eligibility, exposing unresolved overlaps/annexures rather than selecting latest revision.
6. Preserve all adjudication attempts and original clock events in exports; no invented pre/post recall decisions.
7. Separate historical imports from fresh approvals; defensive audit-export snapshots; content-addressed replay manifest.

Then: clean package/Make/Docker paths, output ignores, offset parsing, rejects, safe synthetic CLI fixtures/CI security, advisory-vs-historical comparison, named-case regression and truthful docs. Capture baseline and final evidence outside git. All input cells in all15 sheets are readable; actual scanned document bodies/raw telemetry/old decision snapshots are not supplied.

## Exact non-goals
No live LLM, signing/automatic closure, regulatory submission, production retention/immutable store claim, OCR or inferred handwritten limits, full MDM/precedent/batch ledger, external integrations, residency-certified deployment, real queue scheduler, recreated August2025 audit evidence, reconstructed 214-case recall/invoices, broad infrastructure, fabricated effort hours. Runtime remains an offline deterministic eligibility/advisory replay. Design-only items must be labeled as such. Never push, publish or commit confidential inputs/derived outputs.
