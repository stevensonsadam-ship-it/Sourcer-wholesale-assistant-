diff --git a/sintrix_wholesale_estimator/reporting.py b/sintrix_wholesale_estimator/reporting.py
new file mode 100644
index 0000000000000000000000000000000000000000..3461bb6c8afc885cd83ff2d9a49b0a0158449ba9
--- /dev/null
+++ b/sintrix_wholesale_estimator/reporting.py
@@ -0,0 +1,161 @@
+"""Reporting utilities for generating shareable offer packets."""
+from __future__ import annotations
+
+from pathlib import Path
+from textwrap import wrap
+
+from .models import DealEstimate
+
+PAGE_WIDTH = 612  # 8.5 * 72
+PAGE_HEIGHT = 792  # 11 * 72
+LEFT_MARGIN = 60
+TOP_MARGIN = 720
+LINE_HEIGHT = 14
+
+
+def _pdf_objects(lines: list[str]) -> tuple[list[str], list[int]]:
+    objects: list[str] = []
+    offsets: list[int] = [0]
+
+    header = "%PDF-1.4\n"
+    objects.append(header)
+    offsets.append(len("".join(objects)))
+
+    catalog = "1 0 obj << /Type /Catalog /Pages 2 0 R >> endobj\n"
+    objects.append(catalog)
+    offsets.append(len("".join(objects)))
+
+    pages = "2 0 obj << /Type /Pages /Kids [3 0 R] /Count 1 >> endobj\n"
+    objects.append(pages)
+    offsets.append(len("".join(objects)))
+
+    page = (
+        "3 0 obj << /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] "
+        "/Contents 4 0 R /Resources << /Font << /F1 5 0 R >> >> >> endobj\n"
+    )
+    objects.append(page)
+    offsets.append(len("".join(objects)))
+
+    text_stream = ["BT /F1 11 Tf"]
+    y = TOP_MARGIN
+    for line in lines:
+        safe = line.replace("(", "[").replace(")", "]")
+        text_stream.append(f"1 0 0 1 {LEFT_MARGIN} {y} Tm ({safe}) Tj")
+        y -= LINE_HEIGHT
+        if y < 72:
+            break
+    text_stream.append("ET")
+    stream_body = "\n".join(text_stream)
+    stream = f"4 0 obj << /Length {len(stream_body)} >> stream\n{stream_body}\nendstream endobj\n"
+    objects.append(stream)
+    offsets.append(len("".join(objects)))
+
+    font = "5 0 obj << /Type /Font /Subtype /Type1 /BaseFont /Helvetica >> endobj\n"
+    objects.append(font)
+    offsets.append(len("".join(objects)))
+
+    xref_start = len("".join(objects))
+    xref_lines = ["xref", "0 6", "0000000000 65535 f "]
+    cursor = 0
+    for obj in objects[1:]:
+        xref_lines.append(f"{cursor:010} 00000 n ")
+        cursor += len(obj)
+    xref_lines.append("trailer << /Size 6 /Root 1 0 R >>")
+    xref_lines.append(f"startxref\n{xref_start}\n%%EOF")
+    objects.append("\n".join(xref_lines))
+    return objects, offsets
+
+
+def generate_pdf(estimate: DealEstimate, path: Path) -> Path:
+    """Create a minimalist PDF summary for the estimate."""
+
+    lines: list[str] = [
+        "SOURCER DEAL SNAPSHOT",
+        "",
+        f"Address: {estimate.property.address}, {estimate.property.city} {estimate.property.postal_code}",
+        f"Condition: {estimate.property.condition.replace('_', ' ').title()}",
+        "",
+        f"ARV: ${estimate.insight.arv:,.0f}",
+        f"MAO: ${estimate.insight.mao:,.0f}",
+        f"Recommended Offer: ${estimate.offers[1].offer_price:,.0f}",
+        f"Projected Profit: ${estimate.insight.projected_profit:,.0f}",
+        "",
+        "Repair Budget",
+    ]
+    for item in estimate.repairs:
+        lines.append(
+            f"- {item.trade}: ${item.cost:,.0f} ({item.quantity} {item.unit} @ L{item.labor_rate}/M{item.material_rate})"
+        )
+    lines.append("")
+    lines.append("Offer Bands")
+    for offer in estimate.offers:
+        lines.append(f"- {offer.label}: ${offer.offer_price:,.0f} | {offer.rationale}")
+    lines.append("")
+    lines.append("Comps")
+    for comp in estimate.comps:
+        adj = comp.adjusted_price
+        lines.append(
+            f"- {comp.address} ({comp.square_feet:.0f} sf) sold {comp.sold_date:%b %Y} for ${comp.sold_price:,.0f} | adj ${adj:,.0f}"
+        )
+    lines.append("")
+    lines.append("Negotiation Notes")
+    for script in estimate.negotiation_scripts:
+        lines.extend([f"* {script.title}", *wrap(script.body, 90), ""])  # type: ignore[arg-type]
+    lines.append("Disclaimers")
+    lines.extend(wrap(estimate.disclaimer, 90))
+    lines.append("")
+    lines.append("Citations")
+    for key, value in estimate.citations.items():
+        lines.append(f"- {key}: {value}")
+
+    objects, _ = _pdf_objects(lines)
+    content = "".join(objects)
+    path.write_text(content)
+    return path
+
+
+def render_text(estimate: DealEstimate) -> str:
+    sections = [
+        "=== SOURCER OFFER SUMMARY ===",
+        f"Property: {estimate.property.address}, {estimate.property.city}, {estimate.property.state} {estimate.property.postal_code}",
+        f"Condition: {estimate.property.condition}",
+        f"ARV ${estimate.insight.arv:,.0f} | As-Is ${estimate.insight.as_is:,.0f} | MAO ${estimate.insight.mao:,.0f}",
+        f"Projected Profit: ${estimate.insight.projected_profit:,.0f}",
+        "",
+        "Repair Budget:",
+    ]
+    for item in estimate.repairs:
+        sections.append(
+            f"  - {item.trade}: ${item.cost:,.0f} ({item.quantity} {item.unit}, labor {item.labor_rate}/material {item.material_rate})"
+        )
+    sections.append("")
+    sections.append("Offer Bands:")
+    for offer in estimate.offers:
+        sections.append(f"  - {offer.label}: ${offer.offer_price:,.0f} | {offer.rationale}")
+    sections.append("")
+    sections.append("Comps:")
+    for comp in estimate.comps:
+        sections.append(
+            f"  - {comp.address} ({comp.square_feet:.0f} sf) sold {comp.sold_date:%Y-%m-%d} for ${comp.sold_price:,.0f}, adj ${comp.adjusted_price:,.0f}"
+        )
+    sections.append("")
+    sections.append("Market Trends:")
+    for trend in estimate.market_trends:
+        sections.append(
+            f"  - ZIP {trend.postal_code}: {trend.median_dom} DOM, avg discount {trend.average_discount:.1%}, absorption {trend.absorption_rate:.2f} (source: {trend.source})"
+        )
+    sections.append("")
+    sections.append("Negotiation Scripts:")
+    for script in estimate.negotiation_scripts:
+        sections.append(f"  * {script.title}: {script.body}")
+    sections.append("")
+    sections.append("Disclaimer:")
+    sections.append(f"  {estimate.disclaimer}")
+    sections.append("")
+    sections.append("Citations:")
+    for key, value in estimate.citations.items():
+        sections.append(f"  - {key}: {value}")
+    return "\n".join(sections)
+
+
+__all__ = ["generate_pdf", "render_text"]
