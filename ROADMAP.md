# Build Estimator — Roadmap

## Known Bugs / Gaps
- [ ] Paint tier 1 — when wall_segments are provided, paint area should be calculated
      from wall geometry automatically instead of falling back to the 2x sqft estimate.
      Currently the wall model calculates drywall area per wall but never passes that
      to the paint calculation.

## Planned Features (in priority order)

1. **Paint tier 1 fix** — use wall geometry for paint area when wall_segments provided
2. **Tests** — pytest suite covering happy path, edge cases, validation errors
3. **Frontend** — 2D floor plan tool that sends wall geometry to the API
4. **Deployment** — live URL via Railway, Render, or Fly.io
5. **Database / persistence** — save and retrieve past estimates (Postgres + SQLAlchemy)

## Nice to Have
- `/docs` endpoint polish — add response descriptions and examples to Pydantic models
- Swagger examples for common request payloads
