# Data contracts — implemented versus target

Executable dataclasses are in `prototype/src/adjudication/domain/models.py`; CSV/JSON fields in `reporting/report_builder.py` and `cli.py` are the current API. `Product.key` is tenant+source-row scoped, not an authoritative global pharmaceutical ID. Source identifiers are retained together. Alias observations retain source row, human attribution/date/comment, negative assertions and candidates; these are not automatically qualified master-data approvals.

SOP candidates retain tenant, document family, facility scope, revision dates and annexure location. Multiple effective revisions in the same family conflict; no `ORDER BY effective_from DESC LIMIT1` override is permitted. Unknown free-text facility scope and missing annexure contents abstain. Business applicability uses excursion start (explicit alert fallback), not today's latest revision.

Study metadata eligibility checks tenant ownership, presentation/purpose/readability and relationship qualification, not matching brand text alone. The supplied index has no controlled identifier/strength attestation, so real study pointers remain candidates with STUDY_RELATIONSHIP_UNVERIFIED even when brand/presentation agree. Explicit identifier relationships in synthetic tests exercise the positive path, not a fabricated qualification of company evidence. No validated stability-envelope arithmetic is implemented.

Notification result separates `applicability`, `policy_status`, `notification_evidence`, `status`, optional due time and `source_window_assessment`. Imported `reg_window_hours` is an observation, not an authoritative legal policy. Receipt offset is source evidence, not a submission event made by this tool.

Each source alert produces a parent attempt with one original clock event. A source reopen flag produces a linked attempt; its `REGULATORY_CLOCK_LINKED` contains the original clock snapshot and source event ID. Missing actual recall chronology remains explicit. `HISTORICAL_DISPOSITION_IMPORTED` uses `source_import`; no fresh signature exists and `new_approval` stays null.

The manifest records workbook SHA256, available Git revision, run as-at, rules and reference-policy versions. It is a snapshot manifest, not a bitemporal database. Target evidence blobs, signatures, legal approvals, cumulative batch exposure, invoice links, carrier claims and known-at historical snapshots are not implemented.
