# ChronoConflict

ChronoConflict is now structured as a backend-driven WWII intelligence and strategic simulation platform. The frontend visual identity remains intact, while the backend is reorganized into modular services, PostgreSQL-oriented domain models, deterministic simulation processing, migration scaffolding, and seedable historical reference data.

## Architecture

- `app.py`: lightweight entrypoint using the Flask app factory.
- `src/ww2ops/__init__.py`: application bootstrap, extension wiring, blueprint registration.
- `src/ww2ops/auth/`: authentication routes and session endpoints.
- `src/ww2ops/analytics/`: dashboard-facing data APIs and analytics overview.
- `src/ww2ops/simulation/`: simulation APIs and simulation detail page.
- `src/ww2ops/command/`: leadership dossier APIs.
- `src/ww2ops/intelligence/`: aftermath and war-crimes archival APIs.
- `src/ww2ops/timeline/`: historical timeline APIs.
- `src/ww2ops/services/`: business logic, seed pipeline, and deterministic simulation engine.
- `src/ww2ops/repositories/`: persistence-facing query helpers.
- `src/ww2ops/db/models.py`: normalized relational schema with JSONB-ready columns.
- `migrations/`: Alembic environment and initial schema migration.
- `tests/`: simulation and API coverage.

## Frontend Contract Map

The existing UI is preserved and expects the following routes and JSON payloads:

- `GET /dashboard/`: renders the command dashboard template.
- `GET /dashboard/api/resources`: nation resource payload keyed by nation name.
- `GET /dashboard/api/territories`: map markers for regions and control.
- `GET /dashboard/api/intelligence`: recent intelligence feed entries.
- `GET /dashboard/api/battles`: battle markers and casualty summaries.
- `GET /timeline/` and `GET /timeline/api/events`: chronological battle and operation data.
- `GET /simulation/`, `POST /simulation/start`, `POST /simulation/decision`, `GET /simulation/<id>`.
- `GET /command/`, `GET /command/api/leaders`, `GET /command/api/leaders/<id>`.
- `GET /aftermath/`, `GET /aftermath/api/events`.
- `GET /api/stats`: headline dashboard totals.

Additional backend-oriented endpoints now exist without changing the UI:

- `GET /auth/session`
- `GET /analytics/overview`

## Data Model Summary

Core relational entities implemented:

- `users`
- `alliances`
- `nations`
- `geographic_regions`
- `leaders`
- `campaigns`
- `battles`
- `operations`
- `command_assignments`
- `resource_types`
- `resource_snapshots`
- `resource_balances`
- `intelligence_reports`
- `war_events`
- `war_crimes`
- `timeline_entries`
- `simulations`
- `simulation_decisions`
- `simulation_outcomes`
- `simulation_audit_events`
- `import_batches`

PostgreSQL-specific design choices include JSONB-capable columns, timestamp indexes, simulation-centric lookup indexes, and region coordinate indexes. The migration skeleton is included under `migrations/versions/0001_initial.py`.

## Simulation Engine

The new simulation path is deterministic by seed and stores a decision audit trail:

1. A simulation session is created with a reproducible seed.
2. Each decision is persisted in `simulation_decisions`.
3. The engine applies weighted factors across resources, leadership, morale, and intelligence.
4. A bounded Monte Carlo estimate supplements the weighted score.
5. Outcome, impact payload, and narrative summary are persisted in `simulation_outcomes`.
6. A corresponding audit record and timeline entry are written for traceability.

## Environment Setup

1. Create and activate a virtual environment.
2. Install dependencies with `pip install -r requirements.txt`.
3. Copy `.env.example` to `.env` and update values.
4. Create PostgreSQL database `chrono_conflict`.
5. Run migrations with `flask db upgrade` or standard Alembic commands.
6. Seed reference data with `flask seed-reference-data` if the database is empty.
7. Start the server with `python app.py`.

## Testing

- Unit test: `tests/test_simulation_engine.py`
- Integration-style API test scaffold: `tests/test_api.py`

Run with `pytest` after installing dependencies.

## Notes

- Existing templates, layout, CSS, and frontend behavior are intentionally preserved.
- Current CSRF protection is enabled at the extension level, but legacy auth and simulation routes are exempted so the unchanged UI continues to function.
- The included migration file is a baseline scaffold for the production schema and can be expanded as the historical dataset grows.
