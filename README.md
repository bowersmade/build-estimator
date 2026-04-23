# Build Estimator

A real-time residential construction cost estimation engine. The long-term vision is a browser-based spatial builder — draw walls, place windows and doors, select materials — and get an accurate cost estimate updating live as you design.

The backend API is production-ready. The spatial frontend is in active development.

---

## What it does

You describe a house — square footage, flooring zones, roof type and material, paint, appliances — and the engine returns a fully itemized cost estimate broken down by material category. Every calculation is traceable: the response tells you exactly what area was used, where it came from, and what it cost.

Example request:

```json
POST /estimate
{
  "square_footage": 2000,
  "flooring_zones": [
    { "material": "engineered_hardwood", "sqft": 1200, "room": "main_floor" },
    { "material": "ceramic_tile",        "sqft": 800,  "room": "bathrooms" }
  ],
  "roof": { "type": "gable", "pitch": 6, "material": "architectural_shingles" },
  "paint": { "material": "premium_satin" },
  "appliances": [
    { "appliance": "refrigerator_premium", "quantity": 1 },
    { "appliance": "range_gas",            "quantity": 1 },
    { "appliance": "dishwasher_standard",  "quantity": 1 }
  ]
}
```

Example response (abbreviated):

```json
{
  "materials": 168420.00,
  "permits":   12000.00,
  "total_cost": 180420.00,
  "cost_per_sqft": 90.21,
  "cost_breakdown": { ... },
  "selections": { ... },
  "warnings": []
}
```

---

## Architecture

```
backend/
  app/
    main.py                        # FastAPI app entry point
    models/
      estimate.py                  # Pydantic input/output models
    api/
      routes/
        estimate.py                # POST /estimate — validation + routing
        catalog.py                 # GET /catalog/* — material options
    services/
      cost_engine.py               # Orchestrates all calculations
      calculations.py              # Pure math functions, one per cost category
      datasets/
        st_george.py               # Regional cost data (St. George, UT)
        materials_catalog.py       # All selectable materials and prices

frontend/                          # React + TypeScript — in development
```

**Key design decisions:**

- Regional multiplier applies to construction materials only. Appliances are nationally priced retail goods and are added after the multiplier.
- Flooring is modeled as zones, not whole-house. A 2000 sqft house can have engineered hardwood in 1200 sqft and ceramic tile in 800 sqft, each priced separately.
- Roof area is calculated from floor area × slope factor (derived from pitch) × roof type multiplier. If the Sims engine provides exact sqft, that value is used directly.
- Wall geometry (studs, drywall, sheathing, openings) is the current development focus — see [Wall Model](#wall-model-in-development) below.

---

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/` | Health check |
| POST | `/estimate` | Full cost estimate from house description |
| GET | `/catalog/flooring` | All flooring options and prices |
| GET | `/catalog/roofing` | All roofing options, valid types, pitch range |
| GET | `/catalog/paint` | All paint options and prices |
| GET | `/catalog/appliances` | All appliance options and prices |

---

## Materials

**Flooring** — 9 options from vinyl plank ($3/sqft) to marble tile ($20/sqft)

**Roofing** — 9 options from asphalt 3-tab ($2/sqft) to slate ($22/sqft). Includes flat-roof-only materials (TPO membrane, EPDM rubber) with validation enforced.

**Paint** — 5 finishes from basic flat ($0.20/sqft wall area) to designer premium ($0.90/sqft)

**Appliances** — 12 items priced per unit: refrigerators, ranges, dishwasher, microwave, range hood, washer, dryer, garbage disposal

---

## Regional Data

Currently supports **St. George, UT** (regional cost multiplier: 1.05×).

The architecture is designed for multiple regions — each region is a separate dataset file that plugs into the engine. New regions require no changes to the calculation logic.

Base material costs (per sqft of floor area):

| Category | Cost/sqft |
|----------|-----------|
| Lumber | $35 |
| Concrete | $15 |
| Drywall | $15 |
| Insulation | $8 |
| Windows* | $5 |
| Doors* | $3 |

*Placeholder values — replaced by wall geometry calculations in the next phase.

Permit fees: $8,000 base + $2/sqft.

---

## Wall Model *(in development)*

The current lumber, drywall, insulation, windows, and doors estimates are per-sqft approximations. The wall model replaces them with geometry-accurate calculations.

The engine will accept wall segments from the Sims builder:

```json
{
  "wall_segments": [
    {
      "id": "wall_1",
      "length": 20.0,
      "height": 9.0,
      "type": "exterior",
      "stud_spacing": 16,
      "connected_wall_ids": ["wall_2", "wall_4"],
      "openings": [
        { "type": "window", "width": 3.0, "height": 4.0, "position": 5.0 },
        { "type": "door",   "width": 3.0, "height": 7.0, "position": 12.0 }
      ]
    }
  ]
}
```

For each wall the engine calculates:
- Stud count using `floor(length_inches / spacing_inches) + 1`, adjusted for shared studs at junctions and framing members around openings
- Lumber linear feet: plates (3× wall length) + studs + headers (sized by span) + jack studs + rough sills
- Net surface area per face after subtracting openings → drywall, sheathing, insulation sqft
- Wall type determines which faces get drywall/sheathing/insulation (exterior, interior finished, interior unfinished)

When `wall_segments` is empty the engine falls back to the current per-sqft estimates, so existing requests don't break.

---

## Setup

**Requirements:** Python 3.11+

```bash
cd backend
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

API runs at `http://localhost:8000`. Interactive docs at `http://localhost:8000/docs`.

---

## Planned

- [ ] Wall model — stud counts, lumber LF, drywall/sheathing sqft from geometry
- [ ] React + TypeScript frontend — 2D spatial builder with real-time cost updates
- [ ] Window and door catalogs with per-unit pricing
- [ ] Lumber pricing by board type (2×4, 2×6, LVL beam)
- [ ] Additional regions
- [ ] Test suite
- [ ] Docker + deployment
