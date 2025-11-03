diff --git a/tests/test_estimation_engine.py b/tests/test_estimation_engine.py
new file mode 100644
index 0000000000000000000000000000000000000000..7311ceb6af37219f84c67cca870fc103d3a76a28
--- /dev/null
+++ b/tests/test_estimation_engine.py
@@ -0,0 +1,51 @@
+from sintrix_wholesale_estimator.estimator import EstimationEngine, MarketNotFoundError
+from sintrix_wholesale_estimator.models import DealConfig, SubjectProperty
+
+
+def build_subject() -> SubjectProperty:
+    return SubjectProperty(
+        address="123 Demo St",
+        city="Austin",
+        state="TX",
+        postal_code="78704",
+        square_feet=1850,
+        beds=3,
+        baths=2,
+        condition="light_rehab",
+        property_type="single_family",
+    )
+
+
+def test_estimation_returns_complete_payload(tmp_path):
+    engine = EstimationEngine()
+    config = DealConfig(include_pdf=False)
+    subject = build_subject()
+
+    artifacts = engine.estimate(subject, config)
+
+    assert artifacts.estimate.insight.arv > artifacts.estimate.insight.as_is
+    assert len(artifacts.estimate.offers) == 3
+    assert artifacts.estimate.repairs
+    assert artifacts.estimate.market_trends
+    assert artifacts.pdf_path is None
+    assert "SOURCER OFFER SUMMARY" in artifacts.text_summary
+
+
+def test_unknown_market_raises():
+    engine = EstimationEngine()
+    subject = SubjectProperty(
+        address="1 Unknown",
+        city="Nowhere",
+        state="ZZ",
+        postal_code="99999",
+        square_feet=1500,
+        beds=3,
+        baths=2,
+    )
+
+    try:
+        engine.estimate(subject, DealConfig(include_pdf=False))
+    except MarketNotFoundError as exc:
+        assert "Known markets" in str(exc)
+    else:
+        raise AssertionError("Expected MarketNotFoundError")
