# Crosswalk web workspace

The web app will implement the structure in [`../../docs/ui-structure.md`](../../docs/ui-structure.md).

Initial route map:

| Route | Purpose |
| --- | --- |
| `/projects` | Choose or create an integration project |
| `/projects/:id` | Project home and current work summary |
| `/projects/:id/discover` | Import and inspect an API |
| `/projects/:id/review` | Resolve mapping candidates |
| `/projects/:id/mappings/:mappingId` | Inspect an approved mapping |
| `/projects/:id/runs` | Inspect executions, drift, and repair proposals |

The first implementation target is the project shell, discovery inspection,
and review queue. It should use real API contracts from `apps/api`; fixture
data may be used only to make the loading and empty states visible while the
HTTP client is wired.
