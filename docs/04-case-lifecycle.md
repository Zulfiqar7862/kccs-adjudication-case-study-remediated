# Offline attempt lifecycle

The executable opens an attempt, preserves source facts, evaluates advisory evidence/clock conditions and leaves it `PENDING_REVIEWER`. It imports existing outcomes as historical facts, never as fresh reviewer actions. It does not implement a signed human workbench or state transition API. Source non-actionable classification is parsed separately from closure permission, which is always false in this slice.

All attempts remain in `CaseService.all_attempts`; `create_case` returns the latest attempt for compatibility. A reopen flag adds an attempt linked to the original parent and original clock, never a new regulatory deadline. This preserves what is present in the extract; it cannot recover the original pre-recall outcome if only the latest outcome is supplied. Persistent reopening, optimistic concurrency and recovery are target features.

Future lifecycle: detected → eligible closure OR evidence collection → human review → signed disposition; evidence correction opens a new linked attempt and invalidates affected dependency-derived artefacts without deleting history. Notification proceeds independently throughout. Auto-closure requires a separately approved, tested ruleset; source history never supplies that approval.
