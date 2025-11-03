diff --git a/sintrix_wholesale_estimator/pipeline.py b/sintrix_wholesale_estimator/pipeline.py
new file mode 100644
index 0000000000000000000000000000000000000000..20b69034721b36433fe277d57475faf3931a907c
--- /dev/null
+++ b/sintrix_wholesale_estimator/pipeline.py
@@ -0,0 +1,91 @@
+"""Pipeline persistence helpers."""
+from __future__ import annotations
+
+import csv
+import json
+from dataclasses import asdict
+from datetime import UTC, date, datetime
+from pathlib import Path
+from typing import Iterable, List, Optional
+from urllib import request
+
+from .models import DealEstimate, PipelineRecord, SubjectProperty
+
+DEFAULT_PIPELINE_DIR = Path.home() / ".sintrix"
+DEFAULT_PIPELINE_PATH = DEFAULT_PIPELINE_DIR / "pipeline.json"
+DEFAULT_EXPORT_PATH = DEFAULT_PIPELINE_DIR / "pipeline.csv"
+
+
+def _ensure_directory(path: Path) -> None:
+    path.mkdir(parents=True, exist_ok=True)
+
+
+class PipelineStore:
+    """Lightweight persistence for saved deals."""
+
+    def __init__(self, path: Path | None = None) -> None:
+        self.path = path or DEFAULT_PIPELINE_PATH
+        _ensure_directory(self.path.parent)
+
+    def _load(self) -> List[dict]:
+        if not self.path.exists():
+            return []
+        return json.loads(self.path.read_text())
+
+    def _dump(self, payload: List[dict]) -> None:
+        self.path.write_text(json.dumps(payload, indent=2, default=str))
+
+    def save(self, estimate: DealEstimate, tags: Optional[Iterable[str]] = None) -> PipelineRecord:
+        record = PipelineRecord(
+            property=estimate.property,
+            insight=estimate.insight,
+            created_at=date.today(),
+            tags=tuple(tags or ()),
+        )
+        payload = self._load()
+        payload.append(asdict(record))
+        self._dump(payload)
+        return record
+
+    def export_csv(self, destination: Path | None = None) -> Path:
+        destination = destination or DEFAULT_EXPORT_PATH
+        _ensure_directory(destination.parent)
+        rows = self._load()
+        if not rows:
+            destination.write_text("property_address,city,state,postal_code,mao,arv,created_at\n")
+            return destination
+
+        with destination.open("w", newline="") as handle:
+            writer = csv.writer(handle)
+            writer.writerow(["property_address", "city", "state", "postal_code", "mao", "arv", "created_at"])
+            for row in rows:
+                prop = row["property"]
+                insight = row["insight"]
+                writer.writerow(
+                    [
+                        prop["address"],
+                        prop["city"],
+                        prop["state"],
+                        prop["postal_code"],
+                        insight["mao"],
+                        insight["arv"],
+                        row["created_at"],
+                    ]
+                )
+        return destination
+
+    def send_webhook(self, estimate: DealEstimate, url: str, timeout: float = 5.0) -> int:
+        body = json.dumps(
+            {
+                "property": asdict(estimate.property),
+                "insight": asdict(estimate.insight),
+                "offers": [asdict(offer) for offer in estimate.offers],
+                "timestamp": datetime.now(UTC).isoformat(),
+            }
+        ).encode()
+        req = request.Request(url, data=body, headers={"Content-Type": "application/json"})
+        with request.urlopen(req, timeout=timeout) as response:  # pragma: no cover - network
+            return response.getcode()
+
+
+__all__ = ["PipelineStore"]
