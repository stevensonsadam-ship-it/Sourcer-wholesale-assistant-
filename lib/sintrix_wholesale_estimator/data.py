diff --git a/sintrix_wholesale_estimator/data.py b/sintrix_wholesale_estimator/data.py
index 61dd928cf150801f7b95ecbc62888a713475219d..4eca209537a633f0cce8fe8145fcf377f4cb0bf1 100644
--- a/sintrix_wholesale_estimator/data.py
+++ b/sintrix_wholesale_estimator/data.py
@@ -1,57 +1,113 @@
- (cd "$(git rev-parse --show-toplevel)" && git apply --3way <<'EOF' 
-diff --git a/sintrix_wholesale_estimator/data.py b/sintrix_wholesale_estimator/data.py
-new file mode 100644
-index 0000000000000000000000000000000000000000..4582d03f3a6467348ae119acfcae4c5d546e1312
---- /dev/null
-+++ b/sintrix_wholesale_estimator/data.py
-@@ -0,0 +1,47 @@
-+"""Utilities for loading market data used by the estimator."""
-+from __future__ import annotations
-+
-+import json
-+from dataclasses import dataclass
-+from importlib import resources
-+from typing import Dict, Mapping
-+
-+
-+@dataclass(frozen=True)
-+class MarketProfile:
-+    """Data model representing localized assumptions for an area."""
-+
-+    name: str
-+    price_per_sqft_turnkey: float
-+    condition_adjustment: Mapping[str, float]
-+    property_type_adjustment: Mapping[str, float]
-+    renovation_cost_per_sqft: Mapping[str, float]
-+    closing_cost_rate: float
-+    holding_cost_rate: float
-+    wholesale_fee_rate: float
-+    holding_months: float
-+    demand_index: float
-+
-+
-+def load_market_profiles() -> Dict[str, MarketProfile]:
-+    """Load market profile data bundled with the package."""
-+
-+    path = resources.files(__package__) / "data" / "market_data.json"
-+    raw = json.loads(path.read_text())
-+
-+    profiles: Dict[str, MarketProfile] = {}
-+    for name, payload in raw.items():
-+        profiles[name] = MarketProfile(
-+            name=name,
-+            price_per_sqft_turnkey=payload["price_per_sqft_turnkey"],
-+            condition_adjustment=payload["condition_adjustment"],
-+            property_type_adjustment=payload["property_type_adjustment"],
-+            renovation_cost_per_sqft=payload["renovation_cost_per_sqft"],
-+            closing_cost_rate=payload["closing_cost_rate"],
-+            holding_cost_rate=payload["holding_cost_rate"],
-+            wholesale_fee_rate=payload["wholesale_fee_rate"],
-+            holding_months=payload["holding_months"],
-+            demand_index=payload["demand_index"],
-+        )
-+
-+    return profiles
- 
-EOF
-)
\ No newline at end of file
+"""Static data loading helpers for the estimator."""
+from __future__ import annotations
+
+import json
+from dataclasses import dataclass
+from importlib import resources
+from pathlib import Path
+from typing import Dict, Iterable, Mapping
+
+
+@dataclass(frozen=True)
+class MarketProfile:
+    name: str
+    price_per_sqft_turnkey: float
+    condition_adjustment: Mapping[str, float]
+    property_type_adjustment: Mapping[str, float]
+    renovation_cost_per_sqft: Mapping[str, float]
+    closing_cost_rate: float
+    holding_cost_rate: float
+    wholesale_fee_rate: float
+    holding_months: float
+    demand_index: float
+
+
+@dataclass(frozen=True)
+class ZipCostProfile:
+    postal_code: str
+    labor_rates: Mapping[str, float]
+    material_rates: Mapping[str, float]
+    dom_days: float
+    discount_rate: float
+    absorption_rate: float
+    source: str
+
+
+@dataclass(frozen=True)
+class CompRecordSeed:
+    address: str
+    postal_code: str
+    sold_price: float
+    sold_date: str
+    square_feet: float
+    beds: float
+    baths: float
+    distance_miles: float
+    dom: int
+
+
+def _load_json(package: str, relative: str) -> Mapping[str, object]:
+    package_root = resources.files(package)
+    data_path = package_root / relative
+    if not isinstance(data_path, Path):  # pragma: no cover - importlib nuance
+        data_path = Path(str(data_path))
+    return json.loads(data_path.read_text())
+
+
+def load_market_profiles() -> Dict[str, MarketProfile]:
+    raw = _load_json(__package__, "data/market_data.json")
+    profiles: Dict[str, MarketProfile] = {}
+    for name, payload in raw.items():
+        profiles[name] = MarketProfile(
+            name=name,
+            price_per_sqft_turnkey=payload["price_per_sqft_turnkey"],
+            condition_adjustment=payload["condition_adjustment"],
+            property_type_adjustment=payload["property_type_adjustment"],
+            renovation_cost_per_sqft=payload["renovation_cost_per_sqft"],
+            closing_cost_rate=payload["closing_cost_rate"],
+            holding_cost_rate=payload["holding_cost_rate"],
+            wholesale_fee_rate=payload["wholesale_fee_rate"],
+            holding_months=payload["holding_months"],
+            demand_index=payload["demand_index"],
+        )
+    return profiles
+
+
+def load_zip_cost_profiles() -> Dict[str, ZipCostProfile]:
+    raw = _load_json(__package__, "data/zip_costs.json")
+    profiles: Dict[str, ZipCostProfile] = {}
+    for postal_code, payload in raw.items():
+        profiles[postal_code] = ZipCostProfile(
+            postal_code=postal_code,
+            labor_rates=payload["labor_rates"],
+            material_rates=payload["material_rates"],
+            dom_days=payload["dom_days"],
+            discount_rate=payload["discount_rate"],
+            absorption_rate=payload["absorption_rate"],
+            source=payload["source"],
+        )
+    return profiles
+
+
+def load_comp_seeds() -> Dict[str, Iterable[CompRecordSeed]]:
+    raw = _load_json(__package__, "data/comp_pool.json")
+    pools: Dict[str, Iterable[CompRecordSeed]] = {}
+    for market, entries in raw.items():
+        pools[market] = [
+            CompRecordSeed(
+                address=item["address"],
+                postal_code=item["postal_code"],
+                sold_price=item["sold_price"],
+                sold_date=item["sold_date"],
+                square_feet=item["square_feet"],
+                beds=item["beds"],
+                baths=item["baths"],
+                distance_miles=item["distance_miles"],
+                dom=item["dom"],
+            )
+            for item in entries
+        ]
+    return pools
+
+
+__all__ = [name for name in globals() if name[0].isupper() or name.startswith("load_")]
