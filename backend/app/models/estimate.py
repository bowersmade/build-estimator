from pydantic import BaseModel, Field
from typing import Dict, List, Literal, Optional


class FlooringZone(BaseModel):
    material: str
    sqft: int = Field(gt=0)
    room: Optional[str] = None


class RoofInput(BaseModel):
    type: str
    pitch: Optional[int] = None
    material: str
    sqft: Optional[int] = Field(default=None, gt=0)


class PaintInput(BaseModel):
    material: str
    wall_sqft: Optional[int] = Field(default=None, gt=0)


class ApplianceSelection(BaseModel):
    appliance: str
    quantity: int = Field(default=1, ge=1)


class Opening(BaseModel):
    type: Literal["window", "door"]
    width: float = Field(gt=0)
    height: float = Field(gt=0)
    position: float = Field(ge=0)


class WallSegment(BaseModel):
    id: str
    length: float = Field(gt=0)
    height: float = Field(gt=0)
    type: Literal["exterior", "interior_finished", "interior_unfinished"]
    stud_spacing: Literal[16, 24] = 16
    connected_wall_ids: List[str] = []
    openings: List[Opening] = []


class HouseInput(BaseModel):
    square_footage: int = Field(gt=0)
    flooring_zones: List[FlooringZone] = []
    roof: Optional[RoofInput] = None
    paint: Optional[PaintInput] = None
    appliances: List[ApplianceSelection] = []
    wall_segments: List[WallSegment] = []
    framing_method: Literal["traditional", "advanced"] = "traditional"


class HouseEstimate(BaseModel):
    materials: float
    permits: float
    total_cost: float
    cost_per_sqft: float
    selections: Dict[str, List[str]]
    cost_breakdown: Dict[str, Dict[str, float]]
    warnings: List[str] = []
