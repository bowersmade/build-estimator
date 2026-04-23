BASE_MATERIAL_COSTS = {
    "lumber":      35,
    "concrete":    15,
    "drywall":     15,
    "insulation":   8,
    "windows":      5,
    "doors":        3,
}

PERMIT_FEES = {
    "base":           8000,
    "per_square_foot":   2,
}

# ROOM_COSTS and OPTIONAL_ADDONS are not yet wired into the cost engine.
# They are placeholders for the upcoming wall/room model phase where
# costs will be calculated from actual room geometry instead of total sqft.
ROOM_COSTS = {
    "kitchen": {
        "typical_sqft": 200,
        "materials": {
            "plumbing":    8000,
            "electrical":  5000,
            "finishing":  10000,
        }
    },
    "bathroom": {
        "typical_sqft": 80,
        "materials": {
            "plumbing":   6000,
            "electrical": 1500,
            "finishing":  4000,
        }
    },
    "bedroom": {
        "typical_sqft": 150,
        "materials": {
            "framing":    3000,
            "electrical": 1000,
            "finishing":  2000,
        }
    },
    "living_room": {
        "typical_sqft": 250,
        "materials": {
            "framing":    4000,
            "electrical": 2500,
            "finishing":  6000,
        }
    },
    "garage": {
        "typical_sqft": 400,
        "materials": {
            "framing":    8000,
            "electrical": 2000,
            "finishing":  4000,
        }
    },
    "laundry_room": {
        "typical_sqft": 60,
        "materials": {
            "plumbing":   3000,
            "electrical": 1500,
            "finishing":  2000,
        }
    },
    "office": {
        "typical_sqft": 120,
        "materials": {
            "framing":    2500,
            "electrical": 2000,
            "finishing":  3000,
        }
    },
    "dining_room": {
        "typical_sqft": 150,
        "materials": {
            "framing":    3000,
            "electrical": 1500,
            "finishing":  4000,
        }
    },
    "basement": {
        "typical_sqft": 800,
        "materials": {
            "framing":    12000,
            "electrical":  6000,
            "plumbing":    5000,
            "finishing":  10000,
        }
    },
}

OPTIONAL_ADDONS = {
    "solar": {
        "materials": {
            "electrical": 12000,
        },
        "permits": 1000,
    },
    "garage": {
        "materials": {
            "framing":   8000,
            "finishing": 4000,
        },
        "permits": 1500,
    },
}

REGIONAL_ADJUSTMENTS = {
    "material_cost_multiplier": 1.05,
}
