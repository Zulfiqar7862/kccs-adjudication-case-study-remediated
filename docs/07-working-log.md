# Working Log

## Initial assumptions

### Assumption 1: Rules engine still produces recommendations

**Initial assumption:** `rules_engine_recommendation` was a deterministic rule output.

**Pack evidence:** Since 2024, the field contains the recommendation assistant’s draft, though the column was never renamed.

**Decision:** Treat it as an assistant recommendation; build a separate versioned deterministic-rule path.

### Assumption 2: Product identity resolves from one master record

**Pack evidence:** Product references may be brand names, SKUs, GTINs, or blanks; facility records duplicate physical sites.

**Decision:** Layered identity resolution with exact match, aliases, fuzzy candidates, confidence, and human confirmation.

### Assumption 3: Current master data is sufficient

**Pack evidence:** `spec_text_as_received` can differ from current product master.

**Decision:** Use effective-dated reference data.

### Assumption 4: Regulatory clock follows excursion start

**Pack evidence:** Regulatory clock runs from `alert_ts_utc`; excursion start reflects when product went out of range.

**Decision:** Calculate clock from alert timestamp; retain excursion start as context.

## Discarded approaches

- **End-to-end autonomous AI adjudication:** discarded due to incomplete data, unreadable studies, and audit risk; replaced with human-in-the-loop.
- **Build full MDM first:** discarded because it delays value; replaced with provenance-aware resolution.
- **Treat all timestamps as UTC and discard local context:** discarded because reviewer queue is local time with offset; replaced with UTC canonical plus original local preservation.
- **Single case-status field:** discarded because workflow needs gaps, waits, requests, reopens; replaced with event-sourced lifecycle.

## Lessons learned

- Read the data dictionary before designing the domain model.
- Do not confuse operational latency with compliance deadlines.
- Make uncertainty visible.
- Design for correction, not perfection.
- Separate recommendation from decision.
- Version everything that affects an outcome.
