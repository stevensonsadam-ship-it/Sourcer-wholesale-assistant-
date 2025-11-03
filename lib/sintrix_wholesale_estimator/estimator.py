diff --git a/sintrix_wholesale_estimator/estimator.py b/sintrix_wholesale_estimator/estimator.py
index 8f4de5021d98fe05d21c559e7377f37e16c39a7c..5913fa527db8f1091ba10b135cb6af23d72fd905 100644
--- a/sintrix_wholesale_estimator/estimator.py
+++ b/sintrix_wholesale_estimator/estimator.py
@@ -1,191 +1,212 @@
- (cd "$(git rev-parse --show-toplevel)" && git apply --3way <<'EOF' 
-diff --git a/sintrix_wholesale_estimator/estimator.py b/sintrix_wholesale_estimator/estimator.py
-new file mode 100644
-index 0000000000000000000000000000000000000000..5584d34e9edd69ce6b199e6cbf6ba35c580d3c5f
---- /dev/null
-+++ b/sintrix_wholesale_estimator/estimator.py
-@@ -0,0 +1,181 @@
-+"""Core wholesale estimation logic."""
-+from __future__ import annotations
-+
-+from dataclasses import dataclass
-+from typing import Dict, Mapping, Tuple
-+
-+from .data import MarketProfile, load_market_profiles
-+
-+CONDITION_LEVELS = ("turnkey", "rent_ready", "light_rehab", "heavy_rehab", "tear_down")
-+PROPERTY_TYPES = ("single_family", "multi_family", "condo", "townhome")
-+
-+
-+class MarketNotFoundError(ValueError):
-+    """Raised when a requested market is not defined."""
-+
-+
-+@dataclass
-+class PropertyRequest:
-+    """Input payload describing the subject property."""
-+
-+    location: str
-+    square_feet: float
-+    beds: float
-+    baths: float
-+    condition: str = "light_rehab"
-+    property_type: str = "single_family"
-+    year_built: int | None = None
-+    lot_square_feet: float | None = None
-+    target_assignment_fee: float | None = None
-+
-+
-+@dataclass
-+class PropertyEstimate:
-+    """Output of the wholesale estimator."""
-+
-+    arv: float
-+    as_is_value: float
-+    repair_cost: float
-+    closing_cost: float
-+    holding_cost: float
-+    assignment_fee: float
-+    maximum_allowable_offer: float
-+    recommended_offer: float
-+    projected_profit: float
-+    comparable_range: Tuple[float, float]
-+    confidence: float
-+
-+
-+class WholesaleEstimator:
-+    """Provides wholesale offer guidance based on localized assumptions."""
-+
-+    def __init__(self, market_profiles: Mapping[str, MarketProfile] | None = None) -> None:
-+        self._market_profiles: Mapping[str, MarketProfile] = (
-+            market_profiles if market_profiles is not None else load_market_profiles()
-+        )
-+
-+    @property
-+    def available_markets(self) -> Tuple[str, ...]:
-+        return tuple(sorted(self._market_profiles.keys()))
-+
-+    def estimate(self, request: PropertyRequest) -> PropertyEstimate:
-+        market = self._resolve_market(request.location)
-+        self._validate_inputs(request)
-+
-+        condition = request.condition
-+        property_type = request.property_type
-+
-+        base_price = (
-+            market.price_per_sqft_turnkey
-+            * market.demand_index
-+            * market.property_type_adjustment.get(property_type, 1.0)
-+        )
-+        arv = base_price * request.square_feet
-+
-+        condition_factor = market.condition_adjustment.get(condition)
-+        if condition_factor is None:
-+            raise ValueError(f"Unsupported condition '{condition}'.")
-+
-+        as_is_value = arv * condition_factor
-+
-+        repair_cost = self._estimate_repair_cost(request, market)
-+        closing_cost = market.closing_cost_rate * arv
-+        holding_cost = market.holding_cost_rate * as_is_value * market.holding_months
-+
-+        assignment_fee = self._assignment_fee(request, market, arv)
-+
-+        allowable_discount = 0.72 if condition in {"light_rehab", "heavy_rehab", "tear_down"} else 0.78
-+        maximum_allowable_offer = max(
-+            0.0,
-+            (arv * allowable_discount)
-+            - repair_cost
-+            - closing_cost
-+            - holding_cost
-+            - assignment_fee,
-+        )
-+
-+        recommended_offer = min(maximum_allowable_offer, as_is_value * 0.98)
-+
-+        total_investment = (
-+            recommended_offer + repair_cost + closing_cost + holding_cost + assignment_fee
-+        )
-+        projected_profit = max(0.0, arv - total_investment)
-+
-+        comp_low = as_is_value * 0.92
-+        comp_high = arv * 1.05
-+        confidence = self._confidence_score(market, request)
-+
-+        return PropertyEstimate(
-+            arv=round(arv, 2),
-+            as_is_value=round(as_is_value, 2),
-+            repair_cost=round(repair_cost, 2),
-+            closing_cost=round(closing_cost, 2),
-+            holding_cost=round(holding_cost, 2),
-+            assignment_fee=round(assignment_fee, 2),
-+            maximum_allowable_offer=round(maximum_allowable_offer, 2),
-+            recommended_offer=round(recommended_offer, 2),
-+            projected_profit=round(projected_profit, 2),
-+            comparable_range=(round(comp_low, 2), round(comp_high, 2)),
-+            confidence=round(confidence, 3),
-+        )
-+
-+    def _resolve_market(self, location: str) -> MarketProfile:
-+        try:
-+            return self._market_profiles[location]
-+        except KeyError as exc:  # pragma: no cover - simple guard
-+            available = ", ".join(self.available_markets)
-+            raise MarketNotFoundError(
-+                f"No market profile for '{location}'. Available markets: {available}"
-+            ) from exc
-+
-+    @staticmethod
-+    def _validate_inputs(request: PropertyRequest) -> None:
-+        if request.square_feet <= 0:
-+            raise ValueError("Square footage must be positive.")
-+        if request.beds <= 0:
-+            raise ValueError("Bedroom count must be positive.")
-+        if request.baths <= 0:
-+            raise ValueError("Bathroom count must be positive.")
-+        if request.condition not in CONDITION_LEVELS:
-+            raise ValueError(f"Condition must be one of: {', '.join(CONDITION_LEVELS)}")
-+        if request.property_type not in PROPERTY_TYPES:
-+            raise ValueError(f"Property type must be one of: {', '.join(PROPERTY_TYPES)}")
-+
-+    @staticmethod
-+    def _estimate_repair_cost(request: PropertyRequest, market: MarketProfile) -> float:
-+        per_sqft = market.renovation_cost_per_sqft.get(request.condition, 0.0)
-+        modifier = 1.0
-+        if request.year_built and request.year_built < 1975:
-+            modifier += 0.08
-+        if request.year_built and request.year_built < 1950:
-+            modifier += 0.05
-+        if request.lot_square_feet and request.lot_square_feet > request.square_feet * 2:
-+            modifier += 0.03
-+        return per_sqft * request.square_feet * modifier
-+
-+    @staticmethod
-+    def _assignment_fee(request: PropertyRequest, market: MarketProfile, arv: float) -> float:
-+        if request.target_assignment_fee is not None:
-+            return request.target_assignment_fee
-+        return max(4500.0, arv * market.wholesale_fee_rate)
-+
-+    @staticmethod
-+    def _confidence_score(market: MarketProfile, request: PropertyRequest) -> float:
-+        score = 0.55
-+        score += min(0.1, (market.demand_index - 0.95))
-+        score += min(0.05, market.wholesale_fee_rate)
-+        if request.square_feet <= 900:
-+            score += 0.02
-+        elif request.square_feet <= 1800:
-+            score += 0.05
-+        else:
-+            score += 0.03
-+        if request.condition in {"turnkey", "rent_ready"}:
-+            score += 0.08
-+        elif request.condition == "light_rehab":
-+            score += 0.05
-+        if request.property_type == "single_family":
-+            score += 0.04
-+        elif request.property_type == "multi_family":
-+            score += 0.02
-+        return max(0.3, min(score, 0.92))
- 
-EOF
-)
\ No newline at end of file
+"""Core orchestration for the Sourcer estimation workflow."""
+from __future__ import annotations
+
+from dataclasses import dataclass
+from pathlib import Path
+from statistics import mean
+from typing import Iterable, Mapping, Sequence
+
+from . import comps, repairs
+from .data import CompRecordSeed, MarketProfile, ZipCostProfile, load_comp_seeds, load_market_profiles, load_zip_cost_profiles
+from .models import (
+    DealConfig,
+    DealEstimate,
+    MarketTrend,
+    NegotiationScript,
+    OfferBand,
+    PropertyInsight,
+    SubjectProperty,
+)
+from .reporting import generate_pdf, render_text
+
+
+class MarketNotFoundError(ValueError):
+    """Raised when a property cannot be matched to a market profile."""
+
+
+@dataclass(slots=True)
+class EstimationArtifacts:
+    estimate: DealEstimate
+    pdf_path: str | None
+    text_summary: str
+
+
+class EstimationEngine:
+    """Generates offer guidance, comps, and collateral for a subject property."""
+
+    def __init__(
+        self,
+        markets: Mapping[str, MarketProfile] | None = None,
+        zip_costs: Mapping[str, ZipCostProfile] | None = None,
+        comp_pools: Mapping[str, Sequence[CompRecordSeed]] | None = None,
+    ) -> None:
+        self._markets = markets or load_market_profiles()
+        self._zip_costs = zip_costs or load_zip_cost_profiles()
+        self._comp_pools = comp_pools or load_comp_seeds()
+
+    @property
+    def available_markets(self) -> Sequence[str]:
+        return tuple(sorted(self._markets))
+
+    def _resolve_market(self, subject: SubjectProperty) -> MarketProfile:
+        market = self._markets.get(subject.market_key)
+        if market is None:
+            raise MarketNotFoundError(
+                f"No market profile for '{subject.market_key}'. Known markets: {', '.join(self.available_markets)}"
+            )
+        return market
+
+    def _resolve_zip(self, subject: SubjectProperty, market: MarketProfile) -> ZipCostProfile:
+        profile = self._zip_costs.get(subject.postal_code)
+        if profile is None:
+            # fallback: use first profile for market (matching postal prefix)
+            for candidate in self._zip_costs.values():
+                if candidate.source.startswith(market.name.split(",")[0]):
+                    profile = candidate
+                    break
+        if profile is None:
+            raise MarketNotFoundError(
+                f"No ZIP pricing data for {subject.postal_code}. Provide a supported ZIP or update data tables."
+            )
+        return profile
+
+    def _factor_for_risk(self, config: DealConfig) -> float:
+        base = config.strategy.factor
+        if config.risk_profile == "aggressive":
+            base -= 0.03
+        elif config.risk_profile == "conservative":
+            base += 0.03
+        return max(0.55, min(base, 0.75))
+
+    def _offer_bands(self, mao: float, as_is: float, config: DealConfig) -> list[OfferBand]:
+        buffer = max(5000.0, mao * 0.05)
+        safe_bump = max(6500.0, mao * 0.035)
+        aggressive = max(0.0, mao - buffer)
+        target = max(0.0, mao)
+        safe = min(as_is * 0.97, mao + safe_bump)
+        return [
+            OfferBand(label="Aggressive", offer_price=round(aggressive, 2), mao=round(mao, 2), rationale="Anchors negotiations low"),
+            OfferBand(label="Target", offer_price=round(target, 2), mao=round(mao, 2), rationale="Protects assignment spread"),
+            OfferBand(label="Safe", offer_price=round(safe, 2), mao=round(mao, 2), rationale="Preserves rapport while staying under as-is"),
+        ]
+
+    def _negotiation_scripts(self, subject: SubjectProperty, offers: Iterable[OfferBand], config: DealConfig) -> list[NegotiationScript]:
+        scripts: list[NegotiationScript] = []
+        scripts.append(
+            NegotiationScript(
+                title="Condition & Carry Costs",
+                body=(
+                    f"Given the {subject.condition.replace('_', ' ')} condition we are carrying a repair budget north of $"
+                    f"{config.strategy.assignment_fee:,.0f}. Our target number keeps us safe on holding costs while guaranteeing closing."
+                ),
+            )
+        )
+        scripts.append(
+            NegotiationScript(
+                title="Speed-to-close",
+                body=(
+                    "We can close in 14 days with hard earnest money. If we can land closer to the target band "
+                    "we'll handle all title and inspection logistics."
+                ),
+            )
+        )
+        scripts.append(
+            NegotiationScript(
+                title="Walk-away framing",
+                body=(
+                    "If a higher number is a must, we can explore our safe band but it trims our spread considerably. "
+                    "We'd need flexibility on access or closing timeline to justify it."
+                ),
+            )
+        )
+        return scripts
+
+    def _disclaimer(self) -> str:
+        return (
+            "These values are modeled using public sales records, MLS trend summaries, and internal heuristics. "
+            "Always validate with licensed professionals before making binding offers."
+        )
+
+    def _citations(self, market: MarketProfile, zip_profile: ZipCostProfile) -> dict[str, str]:
+        return {
+            "Market profile": f"Sintrix blended MLS + public record heuristics ({market.name})",
+            "ZIP cost": zip_profile.source,
+        }
+
+    def estimate(self, subject: SubjectProperty, config: DealConfig | None = None) -> EstimationArtifacts:
+        config = config or DealConfig()
+        market = self._resolve_market(subject)
+        zip_profile = self._resolve_zip(subject, market)
+
+        seeds = self._comp_pools.get(subject.market_key, ())
+        comp_records = comps.build_comps(subject, seeds)
+        adjusted_prices = [comp.adjusted_price for comp in comp_records] or [subject.square_feet * market.price_per_sqft_turnkey]
+
+        arv_from_market = subject.square_feet * market.price_per_sqft_turnkey * market.demand_index
+        arv_from_comps = mean(adjusted_prices)
+        arv = (0.55 * arv_from_market) + (0.45 * arv_from_comps)
+
+        as_is = arv * market.condition_adjustment.get(subject.condition, 0.8)
+
+        repair_items = repairs.build_repair_budget(subject, market, zip_profile)
+        repair_total = config.repair_override if config.repair_override is not None else repairs.sum_repair_budget(repair_items)
+
+        closing_rate = config.closing_cost_rate or market.closing_cost_rate
+        holding_months = config.holding_months or market.holding_months
+        holding_cost = as_is * market.holding_cost_rate * holding_months
+        closing_cost = arv * closing_rate
+
+        assignment_fee = config.assignment_fee_override or max(
+            config.strategy.fee_floor,
+            min(config.strategy.fee_ceiling or float("inf"), max(config.strategy.assignment_fee, arv * market.wholesale_fee_rate)),
+        )
+
+        factor = self._factor_for_risk(config)
+        mao = max(0.0, (arv * factor) - repair_total - assignment_fee - closing_cost - holding_cost)
+        offers = self._offer_bands(mao, as_is, config)
+
+        projected_profit = max(0.0, arv - (offers[1].offer_price + repair_total + closing_cost + holding_cost + assignment_fee))
+
+        market_trends = [
+            MarketTrend(
+                postal_code=subject.postal_code,
+                median_dom=zip_profile.dom_days,
+                average_discount=zip_profile.discount_rate,
+                absorption_rate=zip_profile.absorption_rate,
+                source=zip_profile.source,
+            )
+        ]
+
+        insight = PropertyInsight(
+            arv=round(arv, 2),
+            as_is=round(as_is, 2),
+            repair_budget=round(repair_total, 2),
+            closing_costs=round(closing_cost, 2),
+            holding_costs=round(holding_cost, 2),
+            assignment_fee=round(assignment_fee, 2),
+            mao=round(mao, 2),
+            projected_profit=round(projected_profit, 2),
+            demand_score=round(market.demand_index, 2),
+        )
+
+        estimate = DealEstimate(
+            property=subject,
+            insight=insight,
+            offers=offers,
+            comps=comp_records,
+            repairs=repair_items,
+            market_trends=market_trends,
+            negotiation_scripts=self._negotiation_scripts(subject, offers, config),
+            disclaimer=self._disclaimer(),
+            citations=self._citations(market, zip_profile),
+        )
+
+        pdf_path = None
+        if config.include_pdf:
+            output = generate_pdf(estimate, Path.cwd() / "sourcer_offer.pdf")
+            pdf_path = str(output)
+        text_summary = render_text(estimate)
+        return EstimationArtifacts(estimate=estimate, pdf_path=pdf_path, text_summary=text_summary)
+
+
+__all__ = ["EstimationEngine", "EstimationArtifacts", "MarketNotFoundError"]
