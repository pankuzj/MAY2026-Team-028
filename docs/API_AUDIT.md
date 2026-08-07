# SmartSweep API audit

Cross-check performed against `/Users/jatinchakrabarty/Downloads/sprint_plan.html` on 2026-08-07.

## Sprint 1 gaps found and addressed

| Plan contract | Before audit | Result |
| --- | --- | --- |
| `POST /api/v1/complaints/duplicate-check` | Missing | Added authenticated advisory scan using the existing duplicate detector. |
| `POST /api/v1/complaints/{id}/photo` | Only an unscoped upload metadata route existed | Added complaint-scoped validation and attachment. |
| `PATCH /api/v1/tasks/{id}/status` | Missing; generic task patch bypassed lifecycle rules | Added explicit state-machine transitions. |
| `POST /api/v1/tasks/{id}/assistance` | Missing | Added persisted assistance request and migration `0002`. |
| `GET /api/v1/tasks/{id}` | Did not require authentication | Restricted to crew/admin as specified by the plan. |

## Existing implementation confirmed

The repository already contains working auth, ward, complaint CRUD/status/cancel/history,
duplicate listing, high-risk filtering, task create/list/detail/update/complete/cancel, and
resource list/status routes under `/api/v1/resources/*`. These are covered by the existing API
tests and the complaint-to-task integration test.

## Remaining contract drift

The hand-written `docs/sprint-1/openapi.yaml` documents only tasks and resources and does not
yet describe the complete auth, ward, complaint, or newly added endpoints. Resource routes are
also nested under `/api/v1/resources/*`, while the plan lists top-level `/api/v1/workers`,
`/api/v1/equipment`, and `/api/v1/vehicles` paths. These should be resolved in the next API
documentation/compatibility PR rather than silently changing the existing client contract.

The plan's Sprint 2 endpoints (verification, notifications, feedback, feed, reports, bulk
pickups, schedule, and classification) remain unimplemented and were not pulled into this
Sprint 1 change.
