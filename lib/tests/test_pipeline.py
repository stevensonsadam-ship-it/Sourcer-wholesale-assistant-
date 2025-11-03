diff --git a/tests/test_pipeline.py b/tests/test_pipeline.py
new file mode 100644
index 0000000000000000000000000000000000000000..26be2512c9b7710c70be5ecf023f10ba2fda2bde
--- /dev/null
+++ b/tests/test_pipeline.py
@@ -0,0 +1,64 @@
+from pathlib import Path
+
+from sintrix_wholesale_estimator.estimator import EstimationEngine
+from sintrix_wholesale_estimator.models import DealConfig, SubjectProperty
+from sintrix_wholesale_estimator.pipeline import PipelineStore
+
+
+def build_estimate(include_pdf: bool = False):
+    engine = EstimationEngine()
+    subject = SubjectProperty(
+        address="123 Demo St",
+        city="Austin",
+        state="TX",
+        postal_code="78704",
+        square_feet=1850,
+        beds=3,
+        baths=2,
+    )
+    config = DealConfig(include_pdf=include_pdf)
+    return engine.estimate(subject, config)
+
+
+def test_pipeline_save_and_export(tmp_path):
+    artifacts = build_estimate()
+    path = tmp_path / "pipeline.json"
+    store = PipelineStore(path)
+
+    record = store.save(artifacts.estimate, tags=["test", "austin"])
+    assert path.exists()
+
+    export_path = tmp_path / "export.csv"
+    result = store.export_csv(export_path)
+    assert result.exists()
+    content = result.read_text()
+    assert "property_address" in content
+
+
+def test_webhook_payload_serialization(tmp_path, monkeypatch):
+    artifacts = build_estimate()
+    path = tmp_path / "pipeline.json"
+    store = PipelineStore(path)
+
+    class DummyResponse:
+        def __init__(self):
+            self.code = 202
+
+        def getcode(self):
+            return self.code
+
+        def __enter__(self):
+            return self
+
+        def __exit__(self, *args):
+            return False
+
+    def fake_urlopen(req, timeout=5.0):
+        headers = dict(req.header_items())
+        assert headers.get("Content-type") == "application/json"
+        assert req.data
+        return DummyResponse()
+
+    monkeypatch.setattr("sintrix_wholesale_estimator.pipeline.request.urlopen", fake_urlopen)
+    status = store.send_webhook(artifacts.estimate, "https://example.com/webhook")
+    assert status == 202
