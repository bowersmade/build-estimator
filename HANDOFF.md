# Build Estimator — Project Handoff

## What This Project Is

A cost estimation engine for residential home construction. The long-term vision is a Sims-like game where a user draws walls, places windows/doors, selects materials, and gets an accurate real-time cost estimate. Right now the backend API is the focus — no game engine exists yet. A basic frontend UI is planned to test the engine.

The project is located in the `Build Estimator` folder with a `backend/` and `frontend/` directory. The backend runs on FastAPI with Python 3.14.

---

## Project Rules (from CLAUDE.md)

- Be aggressively factual. No fluff.
- Always create proper error handling with good descriptions.
- Follow good code syntax.
- Make everything readable and easy to understand so the next engineer can pick it up quick.
- Explain everything line by line.

---

## File Structure

```
backend/
  app/
    main.py                          # FastAPI app, registers all routers
    models/
      estimate.py                    # All Pydantic input/output models
    api/
      routes/
        estimate.py                  # POST /estimate — main endpoint + validation
        catalog.py                   # GET /catalog/* — returns selectable options
    services/
      cost_engine.py                 # Orchestrates all calculations, builds response
      calculations.py                # Pure math functions, one per cost category
      datasets/
        st_george.py                 # Regional data for St. George, UT
        materials_catalog.py         # All selectable materials and their prices
```

---

## API Endpoints

| Method | Path | What It Does |
|---|---|---|
| GET | `/` | Health check |
| POST | `/estimate` | Takes HouseInput, returns HouseEstimate |
| GET | `/catalog/flooring` | Returns all flooring options |
| GET | `/catalog/roofing` | Returns all roofing options + valid types + pitch range |
| GET | `/catalog/paint` | Returns all paint options |
| GET | `/catalog/appliances` | Returns all appliance options |

---

## Data Models (models/estimate.py)

```python
class FlooringZone(BaseModel):
    material: str          # key from catalog.FLOORING
    sqft: int
    room: Optional[str]    # optional label, e.g. "master_bedroom"

class RoofInput(BaseModel):
    type: str              # flat, gable, hip, shed, gambrel, mansard
    pitch: int             # 0-12 (rise per 12 inches of run)
    material: str          # key from catalog.ROOFING
    sqft: Optional[int]    # if Sims engine provides exact sqft, use it directly

class PaintInput(BaseModel):
    material: str          # key from catalog.PAINT
    wall_sqft: Optional[int]  # if provided use directly, else estimated at floor_sqft x 2.0

class ApplianceSelection(BaseModel):
    appliance: str         # key from catalog.APPLIANCES
    quantity: int = 1

class HouseInput(BaseModel):
    square_footage: int
    flooring_zones: List[FlooringZone] = []   # empty = default vinyl plank full house
    roof: Optional[RoofInput] = None          # None = default gable 6/12 arch shingles
    paint: Optional[PaintInput] = None        # None = default standard eggshell
    appliances: List[ApplianceSelection] = []

class HouseEstimate(BaseModel):
    materials: float
    permits: float
    total_cost: float
    cost_per_sqft: float
    selections: Dict[str, List[str]]          # human-readable summary of what was chosen
    cost_breakdown: Dict[str, Dict[str, float]]
    warnings: List[str] = []
```

---

## How the Engine Works (cost_engine.py)

1. Inject defaults for any missing inputs (flooring, roof, paint)
2. Calculate base material costs from `BASE_MATERIAL_COSTS` per sqft (lumber, concrete, drywall, insulation, windows, doors)
3. Calculate flooring cost by looping zones and looking up catalog prices
4. Calculate roofing cost — if `roof.sqft` provided use it, otherwise calculate from `floor_sqft x slope_factor(pitch) x type_multiplier`
5. Calculate paint cost — if `wall_sqft` provided use it, otherwise estimate as `floor_sqft x 2.0`
6. Apply regional multiplier (1.05 for St. George) to everything above
7. Add appliances AFTER the regional multiplier — appliances are nationally priced retail, not regionally variable
8. Add permit fees
9. Round everything to 2 decimal places via `dollars()` helper at the return statement only

---

## Materials Catalog (materials_catalog.py)

All selectable materials live here. Three pricing types exist:

- **Per sqft of floor area**: flooring, roofing
- **Per sqft of wall area**: paint (wall area is either provided or estimated)
- **Per unit flat price**: appliances

### Flooring (9 options)
vinyl_plank ($3), carpet ($4), laminate ($4), luxury_vinyl_tile ($5), ceramic_tile ($6), engineered_hardwood ($8), porcelain_tile ($8), solid_hardwood_oak ($11), marble_tile ($20)

### Roofing (9 options)
asphalt_3tab ($2), architectural_shingles ($4), corrugated_metal ($6), concrete_tile ($7), standing_seam_metal ($11), clay_tile ($15), slate ($22), tpo_membrane ($5 flat only), epdm_rubber ($4 flat only)

### Paint (5 options)
basic_flat ($0.20), standard_eggshell ($0.35), premium_satin ($0.55), semi_gloss ($0.65), designer_premium ($0.90)

### Appliances (12 options)
refrigerator_standard ($1,200), refrigerator_premium ($2,800), range_electric ($900), range_gas ($1,100), range_professional ($4,500), dishwasher_standard ($600), dishwasher_premium ($1,200), microwave ($250), range_hood ($400), washer ($900), dryer ($900), garbage_disposal ($200)

---

## Regional Data (st_george.py)

Currently the only region. Structure is designed so new regions are separate files that plug in.

```python
BASE_MATERIAL_COSTS = {
    "lumber":     35,   # per sqft of floor area
    "concrete":   15,   # slab assumption — bump to 25+ for basement
    "drywall":    15,
    "insulation":  8,
    "windows":     5,   # PLACEHOLDER — crude per sqft, to be replaced by wall model
    "doors":       3,   # PLACEHOLDER — crude per sqft, to be replaced by wall model
}

PERMIT_FEES = { "base": 8000, "per_square_foot": 2 }

REGIONAL_ADJUSTMENTS = { "material_cost_multiplier": 1.05 }
```

`ROOM_COSTS` and `OPTIONAL_ADDONS` also exist in this file but are NOT currently wired into the engine. They are intentional placeholders for the upcoming wall/room model phase.

---

## Validation (routes/estimate.py)

All validation lives in `validate_house_input()` which runs before the engine. Returns a warnings list that gets merged into the response.

Hard errors (422):
- Invalid flooring material key
- Flooring zones sqft exceeds house sqft
- Invalid roof type
- Invalid roofing material key
- Flat-only material used on pitched roof
- Roof pitch outside 0-12 range
- Invalid paint material key
- Invalid appliance key
- Appliance quantity less than 1

Warnings (pass through but flagged):
- Flooring zones don't cover full house sqft
- Flat roof with pitch > 2/12
- Paint wall_sqft not provided (estimated used)

---

## Known Placeholders / Not Yet Built

1. **Windows and doors are still crude per-sqft estimates** in `BASE_MATERIAL_COSTS`. They will be replaced when the wall model is built.

2. **Paint wall area is estimated** at `floor_sqft x 2.0` when `wall_sqft` isn't provided. Real wall area requires wall geometry.

3. **Only one region exists** (St. George, UT). The architecture supports multiple regions — each region is its own dataset file. No region-switching logic exists yet.

4. **Labor is completely removed** for now. The data structures in `st_george.py` had labor removed intentionally. Labor will be added back once material costs are solid.

5. **`ROOM_COSTS` and `OPTIONAL_ADDONS`** in `st_george.py` are not wired up. Placeholders for the room model phase.

---

## The Next Phase: Wall Model

This is the biggest architectural upgrade planned. Here is the full context.

---

### Core Construction Rules (confirmed by project owner)

**Stud sharing — two types of junctions:**

There are two different ways walls can meet, and they use different stud counts.

**Type 1 — Straight / end-to-end junction:**
Wall A ends, Wall B continues in the same direction right from that point. They share 1 stud. Wall A's last stud IS Wall B's first stud.
- Stud adjustment: subtract 1

**Type 2 — Corner junction (90-degree turn):**
Two walls meet at a right angle. A single shared stud is NOT enough here because drywall on the perpendicular wall needs something to nail to in the inside corner. Two framing methods exist:

- **Traditional corner (default):** 3 studs clustered at the corner. Wall A's last stud + 1 stud turned 90° flat against it + Wall B's first stud. Gives a solid drywall nailer. Most common in residential builds.
- **Advanced framing / California corner:** 2 studs at the corner. Wall A's last stud + Wall B's first stud. A small metal clip or scrap block supports the drywall where there's no stud behind it. Uses 1 less stud per corner, insulates better (no wood blocking insulation in corner cavity), but requires more skill.

The framing method should be a user-selectable option in the Sims builder, defaulting to traditional.

Stud adjustment per corner:
- Traditional: add 2 extra studs per corner (beyond what each wall already counts)
- Advanced framing: add 1 extra stud per corner

**T-intersection (interior wall meeting exterior wall mid-span):**
Add 1 nailer/blocking stud at the junction so drywall has something to attach to.

**Valid stud spacing options (per building code):**
- 16" on center — most common residential
- 24" on center — allowed by code, uses less lumber
- (12" OC exists but is uncommon — confirm with project owner whether to include)

**The stud count formula for one wall:**
```
stud_count = floor(wall_length_inches / stud_spacing_inches) + 1
```

**Lumber is a live running total:**
When a user places walls, a total lumber count (in linear feet) is calculated. When they add a window or door, that number updates — some studs are removed (opening saves lumber) and framing members are added (header, jack studs, rough sill). The net result is almost always MORE lumber after adding an opening, not less.

**Simultaneously, drywall and insulation DROP** when an opening is added because the opening removes surface area from the wall — but only the net area, not the full opening (since framing members reduce the actual opening dimensions slightly).

---

### Wall Types (user-selectable in the Sims UI)

The user selects the wall type when placing it. Three confirmed types:

| Type | Studs | Drywall | Insulation | Sheathing |
|---|---|---|---|---|
| `exterior` | Yes | Interior face only | Yes (cavity) | Yes (exterior face) |
| `interior_finished` | Yes | Both faces | No | No |
| `interior_unfinished` | Yes only | No | No | No |

`interior_unfinished` is used for garage partitions, utility rooms, and any wall where the user doesn't want drywall applied. The user picks this explicitly in the builder — it is NOT auto-detected.

---

### What the Sims game will send

```json
{
  "square_footage": 2000,
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

`connected_wall_ids` tells the engine which walls share a stud at each end so it doesn't double-count.

---

### Stud count calculation per wall

```
Base studs         = floor(length_inches / stud_spacing_inches) + 1
Shared studs       = number of connected walls at endpoints (0, 1, or 2)
Adjusted studs     = base_studs - shared_studs

Per opening — studs removed:
  studs_removed    = floor(opening_width_inches / stud_spacing_inches) - 1

Per opening — framing added:
  jack_studs       = 2 (one each side, height = wall_height - header_depth)
  king_studs       = 2 (full wall height — may already be in base count if at stud position)
  rough_sill       = 1 piece at opening_width (windows only)
  cripples_above   = floor(opening_width_inches / stud_spacing_inches) - 1
  cripples_below   = floor(opening_width_inches / stud_spacing_inches) - 1 (windows only)

Net stud change per opening = -studs_removed + jack_studs + cripples_above + cripples_below
```

---

### Lumber linear feet per wall

```
Plates             = 3 x wall_length  (bottom plate + double top plate)
Stud lumber        = adjusted_stud_count x wall_height
Header lumber      = based on opening width (see table below)
Jack stud lumber   = jack_stud_count x (wall_height - header_depth)
Sill lumber        = opening_width (windows only)

Total linear feet  = plates + studs + headers + jacks + sills
```

---

### Header sizing by span

| Opening Width | Header | Board feet approx |
|---|---|---|
| Under 3ft | Double 2x6 | ~3 LF |
| 3 to 5ft | Double 2x8 | ~5 LF |
| 5 to 7ft | Double 2x10 | ~7 LF |
| 7 to 9ft | Double 2x12 | ~9 LF |
| Over 9ft | Engineered LVL beam | price by span |

---

### Surface area per wall type

```
Gross wall area    = length x height
Net surface area   = gross - sum of all opening areas

Exterior wall:
  drywall          = net surface area x drywall price/sqft  (interior face)
  sheathing        = net surface area x sheathing price/sqft (exterior face)
  insulation       = net surface area x insulation price/sqft (cavity)

Interior finished:
  drywall          = net surface area x 2 (both faces)
  no insulation
  no sheathing

Interior unfinished:
  no drywall
  no insulation
  no sheathing
```

---

### What needs to be built

1. `WallSegment` and `Opening` Pydantic models with all fields above
2. Add `wall_segments: List[WallSegment] = []` to `HouseInput`
3. Window and door catalogs in `materials_catalog.py` (per-unit pricing)
4. Lumber pricing by board type in `materials_catalog.py` (2x4, 2x6, 2x8, 2x10, 2x12, LVL)
5. `calculate_wall_costs(wall_segments)` in `calculations.py` — returns lumber LF, drywall sqft, insulation sqft, sheathing sqft, opening unit costs
6. Remove `windows` and `doors` from `BASE_MATERIAL_COSTS` in `st_george.py`
7. Pull `drywall`, `insulation`, and part of `lumber` out of `BASE_MATERIAL_COSTS` and into wall geometry calculations
8. Wire wall calculations into `cost_engine.py`
9. When `wall_segments` is empty, fall back to current per-sqft estimates so old requests don't break
10. Validation: stud spacing must be 16 or 24, opening width cannot exceed wall length, openings cannot overlap each other

---

### Important note on lumber

Currently `lumber: 35/sqft` is a catch-all for floor framing, wall framing, and roof structure all lumped together. Once wall segments are modeled:
- Wall framing comes from actual stud counts and plate lengths
- Floor framing (joists, beams) still needs its own model eventually
- Roof framing is separate from roofing material (already modeled)
- `lumber` in `BASE_MATERIAL_COSTS` should be reduced to cover only floor framing once walls are done, and eventually removed entirely when floor framing gets its own model too
