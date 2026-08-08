# Sprint 1 API gap test evidence

The added `tests/api/test_sprint_plan_gaps.py` covers the endpoints that were missing from the
implementation/spec cross-check:

- duplicate-check: match returned and unauthenticated access rejected;
- complaint photo: attachment persisted on the complaint;
- task status: valid transition and invalid reverse transition;
- task assistance: persistence and rejection after task closure.

The existing task test was updated so its non-integer path assertion supplies a valid crew token;
task detail is now intentionally protected by the Sprint 1 RBAC contract.
