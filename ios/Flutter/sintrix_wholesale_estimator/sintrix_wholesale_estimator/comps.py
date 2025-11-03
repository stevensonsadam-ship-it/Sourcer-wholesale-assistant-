"""Comparable sale synthesis utilities."""
from __future__ import annotations

from datetime import date
from typing import Iterable, List

from .data import CompRecordSeed
from .models import CompAdjustment, CompRecord, SubjectProperty


def _parse_date(value: str) -> date:
    year, month, day = value.split("-")
    return date(int(year), int(month), int(day))


def _condition_adjustment(subject_condition: str) -> float:
    return {
        "turnkey": 0.02,
        "rent_ready": -0.01,
        "light_rehab": -0.04,
        "heavy_rehab": -0.08,
        "tear_down": -0.12,
    }.get(subject_condition, -0.04)


def build_comps(subject: SubjectProperty, seeds: Iterable[CompRecordSeed]) -> List[CompRecord]:
    comps: List[CompRecord] = []
    condition_adj = _condition_adjustment(subject.condition)
    for seed in seeds:
        adjustments: List[CompAdjustment] = []
        size_delta = subject.square_feet - seed.square_feet
        if abs(size_delta) > 50:
            adjustments.append(
                CompAdjustment(
                    label="Size adjustment",
                    amount=size_delta * 45.0,  # $45 psf heuristic
                )
            )
        bed_delta = subject.beds - seed.beds
        if bed_delta:
            adjustments.append(
                CompAdjustment(
                    label="Bedroom count",
                    amount=bed_delta * 7500.0,
                )
            )
        bath_delta = subject.baths - seed.baths
        if bath_delta:
            adjustments.append(
                CompAdjustment(
                    label="Bathroom count",
                    amount=bath_delta * 6200.0,
                )
            )
        adjustments.append(
            CompAdjustment(
                label="Condition",
                amount=seed.sold_price * condition_adj,
            )
        )
        comps.append(
            CompRecord(
                address=seed.address,
                postal_code=seed.postal_code,
                sold_price=seed.sold_price,
                sold_date=_parse_date(seed.sold_date),
                square_feet=seed.square_feet,
                beds=seed.beds,
                baths=seed.baths,
                distance_miles=seed.distance_miles,
                dom=seed.dom,
                adjustments=adjustments,
            )
        )
    return comps


__all__ = ["build_comps"]
