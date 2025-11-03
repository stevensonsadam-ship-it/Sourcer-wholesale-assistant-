diff --git a/sintrix_wholesale_estimator/cli.py b/sintrix_wholesale_estimator/cli.py
new file mode 100644
index 0000000000000000000000000000000000000000..f5dddd5860bbc98c7ee270b3f70e5b32ac14dd83
--- /dev/null
+++ b/sintrix_wholesale_estimator/cli.py
@@ -0,0 +1,135 @@
+"""Command line interface for the Sourcer wholesale assistant."""
+from __future__ import annotations
+
+import argparse
+import json
+from dataclasses import asdict
+from typing import Iterable
+
+from .estimator import EstimationEngine, EstimationArtifacts, MarketNotFoundError
+from .models import AssignmentStrategy, DealConfig, SubjectProperty
+from .pipeline import PipelineStore
+
+
+def _comma_separated(value: str) -> Iterable[str]:
+    return [chunk.strip() for chunk in value.split(",") if chunk.strip()]
+
+
+def build_parser() -> argparse.ArgumentParser:
+    parser = argparse.ArgumentParser(
+        description="Generate a complete wholesale offer packet from an address or listing URL.",
+    )
+    parser.add_argument("address", help="Street address or property label.")
+    parser.add_argument("city", help="City for the subject property.")
+    parser.add_argument("state", help="Two-letter state code.")
+    parser.add_argument("postal_code", help="5-digit ZIP code.")
+    parser.add_argument("square_feet", type=float, help="Heated square footage.")
+    parser.add_argument("beds", type=float, help="Bedroom count.")
+    parser.add_argument("baths", type=float, help="Bathroom count.")
+    parser.add_argument("--listing-url", help="Optional listing URL to stash with the deal.")
+    parser.add_argument("--condition", default="light_rehab", choices=[
+        "turnkey",
+        "rent_ready",
+        "light_rehab",
+        "heavy_rehab",
+        "tear_down",
+    ])
+    parser.add_argument("--property-type", default="single_family", choices=[
+        "single_family",
+        "multi_family",
+        "condo",
+        "townhome",
+    ])
+    parser.add_argument("--year-built", type=int)
+    parser.add_argument("--lot-square-feet", type=float)
+    parser.add_argument("--factor", type=float, default=0.65, help="MAO factor (0.55-0.75).")
+    parser.add_argument("--assignment-fee", type=float, default=10000.0, help="Target assignment fee if not overriding.")
+    parser.add_argument("--assignment-fee-override", type=float, help="Force a specific assignment fee.")
+    parser.add_argument("--closing-rate", type=float, help="Override closing cost rate (as decimal).")
+    parser.add_argument("--holding-months", type=float, help="Override holding months assumption.")
+    parser.add_argument("--repair-override", type=float, help="Override the calculated repair budget.")
+    parser.add_argument("--risk-profile", choices=["aggressive", "balanced", "conservative"], default="balanced")
+    parser.add_argument("--no-pdf", action="store_true", help="Skip PDF generation.")
+    parser.add_argument("--save", action="store_true", help="Persist the deal into the local pipeline store.")
+    parser.add_argument("--tags", type=_comma_separated, help="Comma-separated tag list used when saving.")
+    parser.add_argument("--export-csv", action="store_true", help="Export the pipeline CSV after saving.")
+    parser.add_argument("--webhook", help="Optional webhook URL to POST deal summaries to.")
+    parser.add_argument("--as-json", action="store_true", help="Return JSON instead of formatted text.")
+    return parser
+
+
+def _build_subject(args: argparse.Namespace) -> SubjectProperty:
+    return SubjectProperty(
+        address=args.address,
+        city=args.city,
+        state=args.state,
+        postal_code=args.postal_code,
+        square_feet=args.square_feet,
+        beds=args.beds,
+        baths=args.baths,
+        year_built=args.year_built,
+        lot_square_feet=args.lot_square_feet,
+        condition=args.condition,
+        property_type=args.property_type,
+        listing_url=args.listing_url,
+    )
+
+
+def _build_config(args: argparse.Namespace) -> DealConfig:
+    strategy = AssignmentStrategy(factor=args.factor, assignment_fee=args.assignment_fee)
+    return DealConfig(
+        strategy=strategy,
+        risk_profile=args.risk_profile,
+        repair_override=args.repair_override,
+        closing_cost_rate=args.closing_rate,
+        holding_months=args.holding_months,
+        assignment_fee_override=args.assignment_fee_override,
+        include_pdf=not args.no_pdf,
+    )
+
+
+def _export_pipeline(store: PipelineStore, args: argparse.Namespace, artifacts: EstimationArtifacts) -> None:
+    if args.save:
+        record = store.save(artifacts.estimate, tags=args.tags or ())
+        if args.export_csv:
+            path = store.export_csv()
+            print(f"Pipeline CSV exported to {path}")
+        if args.webhook:
+            try:
+                code = store.send_webhook(artifacts.estimate, args.webhook)
+                print(f"Webhook delivered with status {code}")
+            except Exception as exc:  # pragma: no cover - network
+                print(f"Webhook failed: {exc}")
+
+
+def run(argv: list[str] | None = None) -> EstimationArtifacts:
+    parser = build_parser()
+    args = parser.parse_args(argv)
+
+    subject = _build_subject(args)
+    config = _build_config(args)
+    engine = EstimationEngine()
+
+    try:
+        artifacts = engine.estimate(subject, config)
+    except MarketNotFoundError as exc:
+        parser.error(str(exc))
+
+    if args.save:
+        store = PipelineStore()
+        _export_pipeline(store, args, artifacts)
+
+    if args.as_json:
+        payload = asdict(artifacts.estimate)
+        if artifacts.pdf_path:
+            payload["pdf_path"] = artifacts.pdf_path
+        print(json.dumps(payload, indent=2, default=str))
+    else:
+        print(artifacts.text_summary)
+        if artifacts.pdf_path:
+            print(f"PDF saved to {artifacts.pdf_path}")
+
+    return artifacts
+
+
+__all__ = ["run", "build_parser"]
