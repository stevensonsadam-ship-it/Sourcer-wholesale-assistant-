diff --git a/tests/conftest.py b/tests/conftest.py
index f0f84089cf7d09d69f0c66e17ec022060ea42089..2a855d9fdb8debae0b082088580a4c41e499e33c 100644
--- a/tests/conftest.py
+++ b/tests/conftest.py
@@ -1,16 +1,6 @@
- (cd "$(git rev-parse --show-toplevel)" && git apply --3way <<'EOF' 
-diff --git a/tests/conftest.py b/tests/conftest.py
-new file mode 100644
-index 0000000000000000000000000000000000000000..2a855d9fdb8debae0b082088580a4c41e499e33c
---- /dev/null
-+++ b/tests/conftest.py
-@@ -0,0 +1,6 @@
-+import sys
-+from pathlib import Path
-+
-+ROOT = Path(__file__).resolve().parents[1]
-+if str(ROOT) not in sys.path:
-+    sys.path.insert(0, str(ROOT))
- 
-EOF
-)
\ No newline at end of file
+import sys
+from pathlib import Path
+
+ROOT = Path(__file__).resolve().parents[1]
+if str(ROOT) not in sys.path:
+    sys.path.insert(0, str(ROOT))
