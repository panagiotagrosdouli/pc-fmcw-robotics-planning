"""Pareto-frontier helpers for reliability-mobility trade-off analysis."""

from __future__ import annotations


def pareto_efficient(points):
    """Return a boolean mask for 2-D minimization Pareto efficiency."""
    pts = [tuple(map(float, p)) for p in points]
    mask = []
    for i, p in enumerate(pts):
        dominated = False
        for j, q in enumerate(pts):
            if i == j:
                continue
            if q[0] <= p[0] and q[1] <= p[1] and (q[0] < p[0] or q[1] < p[1]):
                dominated = True
                break
        mask.append(not dominated)
    return mask
