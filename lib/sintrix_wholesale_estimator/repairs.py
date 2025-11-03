diff --git a/sintrix_wholesale_estimator/repairs.py b/sintrix_wholesale_estimator/repairs.py
new file mode 100644
index 0000000000000000000000000000000000000000..79f39847d5b024a0667361d0eb25049a871defc7
--- /dev/null
+++ b/sintrix_wholesale_estimator/repairs.py
@@ -0,0 +1,73 @@
+"""Repair budget modeling."""
+from __future__ import annotations
+
+from typing import Dict, Iterable, List, Tuple
+
+from .data import MarketProfile, ZipCostProfile
+from .models import RepairLineItem, SubjectProperty
+
+TRADE_DISPLAY = {
+    "roofing": "Roofing & Structure",
+    "hvac": "HVAC",
+    "plumbing": "Plumbing",
+    "electrical": "Electrical",
+    "interior": "Interior Finish",
+    "exterior": "Exterior & Windows",
+    "landscaping": "Landscaping",
+    "contingency": "Contingency",
+}
+
+CONDITION_MULTIPLIERS: Dict[str, float] = {
+    "turnkey": 0.25,
+    "rent_ready": 0.45,
+    "light_rehab": 0.85,
+    "heavy_rehab": 1.25,
+    "tear_down": 1.75,
+}
+
+
+def _quantity(subject: SubjectProperty, trade: str) -> Tuple[float, str]:
+    if trade == "landscaping":
+        lot = subject.lot_square_feet or subject.square_feet * 1.2
+        return lot / 500.0, "500 sq ft lots"
+    return subject.square_feet, "sq ft"
+
+
+def build_repair_budget(
+    subject: SubjectProperty,
+    market: MarketProfile,
+    zip_profile: ZipCostProfile,
+) -> List[RepairLineItem]:
+    multiplier = CONDITION_MULTIPLIERS.get(subject.condition, 0.85)
+    repairs: List[RepairLineItem] = []
+
+    for trade_key, label in TRADE_DISPLAY.items():
+        quantity, unit = _quantity(subject, trade_key)
+        labor = zip_profile.labor_rates.get(trade_key, 0.0)
+        material = zip_profile.material_rates.get(trade_key, 0.0)
+        base_cost = (labor + material) * quantity
+
+        if trade_key == "contingency":
+            base_cost += market.renovation_cost_per_sqft.get("light_rehab", 18.0) * 0.1
+
+        total = base_cost * multiplier
+        repairs.append(
+            RepairLineItem(
+                trade=label,
+                description=f"{label} scope tuned for {subject.condition.replace('_', ' ')}",
+                quantity=round(quantity, 2),
+                unit=unit,
+                labor_rate=round(labor, 2),
+                material_rate=round(material, 2),
+                cost=round(total, 2),
+            )
+        )
+
+    return repairs
+
+
+def sum_repair_budget(items: Iterable[RepairLineItem]) -> float:
+    return sum(item.cost for item in items)
+
+
+__all__ = ["build_repair_budget", "sum_repair_budget"]
