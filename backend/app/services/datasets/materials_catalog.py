FLOORING = {
    "vinyl_plank": {
        "display_name": "Vinyl Plank",
        "price_per_sqft": 3,
    },
    "carpet": {
        "display_name": "Carpet",
        "price_per_sqft": 4,
    },
    "laminate": {
        "display_name": "Laminate",
        "price_per_sqft": 4,
    },
    "luxury_vinyl_tile": {
        "display_name": "Luxury Vinyl Tile (LVT)",
        "price_per_sqft": 5,
    },
    "ceramic_tile": {
        "display_name": "Ceramic Tile",
        "price_per_sqft": 6,
    },
    "engineered_hardwood": {
        "display_name": "Engineered Hardwood",
        "price_per_sqft": 8,
    },
    "porcelain_tile": {
        "display_name": "Porcelain Tile",
        "price_per_sqft": 8,
    },
    "solid_hardwood_oak": {
        "display_name": "Solid Hardwood (Oak)",
        "price_per_sqft": 11,
    },
    "marble_tile": {
        "display_name": "Marble Tile",
        "price_per_sqft": 20,
    },
}

ROOFING = {
    "asphalt_3tab": {
        "display_name": "Asphalt Shingles (3-Tab)",
        "price_per_sqft": 2,
    },
    "architectural_shingles": {
        "display_name": "Architectural Shingles",
        "price_per_sqft": 4,
    },
    "corrugated_metal": {
        "display_name": "Corrugated Metal",
        "price_per_sqft": 6,
    },
    "standing_seam_metal": {
        "display_name": "Standing Seam Metal",
        "price_per_sqft": 11,
    },
    "concrete_tile": {
        "display_name": "Concrete Tile",
        "price_per_sqft": 7,
    },
    "clay_tile": {
        "display_name": "Clay Tile",
        "price_per_sqft": 15,
    },
    "slate": {
        "display_name": "Slate",
        "price_per_sqft": 22,
    },
    "tpo_membrane": {
        "display_name": "TPO Membrane (Flat Roofs Only)",
        "price_per_sqft": 5,
        "flat_only": True,
    },
    "epdm_rubber": {
        "display_name": "EPDM Rubber (Flat Roofs Only)",
        "price_per_sqft": 4,
        "flat_only": True,
    },
}

PAINT = {
    "basic_flat": {
        "display_name": "Basic Flat Paint",
        "price_per_sqft": 0.20,
    },
    "standard_eggshell": {
        "display_name": "Standard Eggshell",
        "price_per_sqft": 0.35,
    },
    "premium_satin": {
        "display_name": "Premium Satin",
        "price_per_sqft": 0.55,
    },
    "semi_gloss": {
        "display_name": "Semi-Gloss",
        "price_per_sqft": 0.65,
    },
    "designer_premium": {
        "display_name": "Designer Premium",
        "price_per_sqft": 0.90,
    },
}

APPLIANCES = {
    "refrigerator_standard": {
        "display_name": "Refrigerator (Standard)",
        "unit_price": 1200,
    },
    "refrigerator_premium": {
        "display_name": "Refrigerator (Premium)",
        "unit_price": 2800,
    },
    "range_electric": {
        "display_name": "Electric Range / Oven",
        "unit_price": 900,
    },
    "range_gas": {
        "display_name": "Gas Range / Oven",
        "unit_price": 1100,
    },
    "range_professional": {
        "display_name": "Professional Range",
        "unit_price": 4500,
    },
    "dishwasher_standard": {
        "display_name": "Dishwasher (Standard)",
        "unit_price": 600,
    },
    "dishwasher_premium": {
        "display_name": "Dishwasher (Premium)",
        "unit_price": 1200,
    },
    "microwave": {
        "display_name": "Microwave",
        "unit_price": 250,
    },
    "range_hood": {
        "display_name": "Range Hood",
        "unit_price": 400,
    },
    "washer": {
        "display_name": "Washer",
        "unit_price": 900,
    },
    "dryer": {
        "display_name": "Dryer",
        "unit_price": 900,
    },
    "garbage_disposal": {
        "display_name": "Garbage Disposal",
        "unit_price": 200,
    },
}

# Extra multiplier per roof type on top of the pitch slope factor.
# Gable and shed are the baseline (1.0). Hip roofs have more surface
# area due to four sloping sides. Mansard has a very steep lower slope
# which adds significant extra surface.
ROOF_TYPE_MULTIPLIERS = {
    "flat":     1.0,
    "shed":     1.0,
    "gable":    1.0,
    "hip":      1.04,
    "gambrel":  1.0,
    "mansard":  1.12,
}

# Multiplier used to estimate total paintable wall area from floor sqft
# when exact wall dimensions aren't available.
# A typical home has roughly 2x its floor area in paintable wall surface.
# This is a known rough estimate — replaced by real geometry from the Sims engine.
WALL_AREA_ESTIMATE_MULTIPLIER = 2.0
