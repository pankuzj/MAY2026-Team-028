## What

<!-- One or two sentences. What does this change, and why now? -->

## Task ID

<!-- From SPRINT_PLAN.md sections 9/10, e.g. S1-A03. One PR should map to one task. -->

S1-

## User stories covered

<!-- The US-xx ids from SPRINT_PLAN.md section 3. These must match the
     x-user-story field in openapi.yaml for the endpoints touched. -->

US-

## How to verify

<!-- The exact commands a reviewer should run. Not "it works" — the steps.
     e.g. `uv run pytest tests/api/test_complaints.py -v`
          curl -X POST localhost:8000/api/v1/complaints -d '{...}' -->

## Checklist

- [ ] Matches `docs/sprint-N/openapi.yaml` — path, request/response schema, status codes
- [ ] Input validation and error handling on every path, using the typed errors in `app/core/exceptions.py`
- [ ] Layer boundaries respected: routes → services → repositories → models, never skipping
- [ ] No `os.environ` outside `app/core/config.py`
- [ ] Tests added — happy path plus at least two failure/edge cases
- [ ] `uv run pytest` green locally
- [ ] `uv run ruff check . && uv run black --check .` clean
- [ ] New model modules added to `app/db/base_models.py` (or Alembic will not see them)
- [ ] `docs/sprint-N/test_cases.md` rows updated with real `Actual Output`

## Notes for the reviewer

<!-- Anything deliberately left out, a decision you want challenged, or a
     known-rough edge with a follow-up task id. -->
