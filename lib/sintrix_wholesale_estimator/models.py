diff --git a/sintrix_wholesale_estimator/models.py b/sintrix_wholesale_estimator/models.py
new file mode 100644
index 0000000000000000000000000000000000000000..69d149132ac07d132a498bf009f8ebb80b988190
--- /dev/null
+++ b/sintrix_wholesale_estimator/models.py
@@ -0,0 +1,172 @@
+"""Dataclasses describing the Sourcer domain model."""
+from __future__ import annotations
+
+from dataclasses import dataclass, field
+from datetime import date
+from typing import Dict, Iterable, List, Optional
+
+
+@dataclass(slots=True)
+class SubjectProperty:
+    """Normalized representation of the subject property."""
+
+    address: str
+    city: str
+    state: str
+    postal_code: str
+    square_feet: float
+    beds: float
+    baths: float
+    year_built: Optional[int] = None
+    lot_square_feet: Optional[float] = None
+    condition: str = "light_rehab"
+    property_type: str = "single_family"
+    listing_url: Optional[str] = None
+
+    @property
+    def market_key(self) -> str:
+        return f"{self.city}, {self.state}".strip().replace("  ", " ")
+
+
+@dataclass(slots=True)
+class AssignmentStrategy:
+    """Configuration for assignment fee calculations."""
+
+    factor: float = 0.65
+    assignment_fee: float = 10000.0
+    fee_floor: float = 4500.0
+    fee_ceiling: Optional[float] = None
+
+    def clamp_factor(self) -> None:
+        self.factor = max(0.55, min(self.factor, 0.75))
+
+
+@dataclass(slots=True)
+class DealConfig:
+    """Configuration values used across the estimation workflow."""
+
+    strategy: AssignmentStrategy = field(default_factory=AssignmentStrategy)
+    risk_profile: str = "balanced"  # aggressive | balanced | conservative
+    repair_override: Optional[float] = None
+    closing_cost_rate: Optional[float] = None
+    holding_months: Optional[float] = None
+    assignment_fee_override: Optional[float] = None
+    include_pdf: bool = True
+
+    def __post_init__(self) -> None:
+        self.strategy.clamp_factor()
+        self.risk_profile = self.risk_profile.lower()
+
+
+@dataclass(slots=True)
+class CompAdjustment:
+    """Adjustments applied to a comparable sale."""
+
+    label: str
+    amount: float
+
+
+@dataclass(slots=True)
+class CompRecord:
+    """Comparable sale information with adjustments."""
+
+    address: str
+    postal_code: str
+    sold_price: float
+    sold_date: date
+    square_feet: float
+    beds: float
+    baths: float
+    distance_miles: float
+    dom: int
+    adjustments: List[CompAdjustment] = field(default_factory=list)
+
+    @property
+    def adjusted_price(self) -> float:
+        return self.sold_price + sum(adj.amount for adj in self.adjustments)
+
+
+@dataclass(slots=True)
+class RepairLineItem:
+    """Line item representing a repair scope."""
+
+    trade: str
+    description: str
+    quantity: float
+    unit: str
+    labor_rate: float
+    material_rate: float
+    cost: float
+
+
+@dataclass(slots=True)
+class OfferBand:
+    """Offer recommendation bucket."""
+
+    label: str
+    offer_price: float
+    mao: float
+    rationale: str
+
+
+@dataclass(slots=True)
+class MarketTrend:
+    """Market-level stats for DOM and discounting."""
+
+    postal_code: str
+    median_dom: float
+    average_discount: float
+    absorption_rate: float
+    source: str
+
+
+@dataclass(slots=True)
+class NegotiationScript:
+    """Negotiation talking points tailored to the scenario."""
+
+    title: str
+    body: str
+
+
+@dataclass(slots=True)
+class PropertyInsight:
+    """High level summary of the subject property and market."""
+
+    arv: float
+    as_is: float
+    repair_budget: float
+    closing_costs: float
+    holding_costs: float
+    assignment_fee: float
+    mao: float
+    projected_profit: float
+    demand_score: float
+
+
+@dataclass(slots=True)
+class DealEstimate:
+    """Complete estimation output."""
+
+    property: SubjectProperty
+    insight: PropertyInsight
+    offers: List[OfferBand]
+    comps: List[CompRecord]
+    repairs: List[RepairLineItem]
+    market_trends: List[MarketTrend]
+    negotiation_scripts: List[NegotiationScript]
+    disclaimer: str
+    citations: Dict[str, str]
+
+
+@dataclass(slots=True)
+class PipelineRecord:
+    """Saved deal state for CRM/pipeline sync."""
+
+    property: SubjectProperty
+    insight: PropertyInsight
+    created_at: date
+    tags: Iterable[str] = field(default_factory=list)
+    crm_url: Optional[str] = None
+
+
+__all__ = [name for name in globals() if not name.startswith("_")]
