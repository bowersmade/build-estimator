from pydantic import BaseModel, Field
from typing import Dict, List, Optional


class FlooringZone(BaseModel):
    material: str
    # Must be > 0 — a zone with 0 or negative sqft is nonsensical and would silently
    # subtract cost or do nothing. Pydantic returns a 422 automatically if violated.
    sqft: int = Field(gt=0, description="Square footage of this flooring zone. Must be greater than 0.")
    room: Optional[str] = None


class RoofInput(BaseModel):
    type: str
    # Pitch is optional. The Sims engine always sends exact roof sqft, so pitch is only
    # needed as a fallback when sqft is not provided (e.g., API-only requests without
    # a game engine). When None and sqft is also absent, the engine defaults to 6/12.
    pitch: Optional[int] = None
    material: str
    # Optional — only provided when the Sims engine has exact roof geometry.
    # If provided, must be > 0. Pydantic applies gt=0 only when a value is given, not when None.
    sqft: Optional[int] = Field(default=None, gt=0, description="Exact roof sqft if known. Must be greater than 0 if provided.")


class PaintInput(BaseModel):
    material: str
    # Same pattern as RoofInput.sqft — optional, but must be > 0 if the caller provides it.
    wall_sqft: Optional[int] = Field(default=None, gt=0, description="Exact wall sqft if known. Must be greater than 0 if provided.")


class ApplianceSelection(BaseModel):
    appliance: str
    # ge=1 means "greater than or equal to 1". You can't install zero or negative appliances.
    # The route also validates this, but enforcing it here means the model itself is honest
    # about what values are valid, not just the validation function.
    quantity: int = Field(default=1, ge=1, description="Number of this appliance to include. Must be at least 1.")


class HouseInput(BaseModel):
    # gt=0 prevents zero (which causes divide-by-zero in cost_per_sqft) and negative values
    # (which produce negative costs). Without this, posting square_footage=0 returns a 500.
    square_footage: int = Field(gt=0, description="Total floor area of the house in square feet. Must be greater than 0.")
    flooring_zones: List[FlooringZone] = []
    roof: Optional[RoofInput] = None
    paint: Optional[PaintInput] = None
    appliances: List[ApplianceSelection] = []


class HouseEstimate(BaseModel):
    materials: float
    permits: float
    total_cost: float
    cost_per_sqft: float
    selections: Dict[str, List[str]]
    cost_breakdown: Dict[str, Dict[str, float]]
    warnings: List[str] = []
