diff --git a/tests/test_cli.py b/tests/test_cli.py
new file mode 100644
index 0000000000000000000000000000000000000000..c6786e496ab3961eda7c9dde9e9781d4f3413705
--- /dev/null
+++ b/tests/test_cli.py
@@ -0,0 +1,23 @@
+import json
+
+from sintrix_wholesale_estimator.cli import run
+
+
+def test_cli_json_output(capsys):
+    argv = [
+        "123 Demo St",
+        "Austin",
+        "TX",
+        "78704",
+        "1850",
+        "3",
+        "2",
+        "--no-pdf",
+        "--as-json",
+    ]
+    artifacts = run(argv)
+    captured = capsys.readouterr()
+    data = json.loads(captured.out)
+
+    assert data["insight"]["mao"] == artifacts.estimate.insight.mao
+    assert len(data["offers"]) == 3
