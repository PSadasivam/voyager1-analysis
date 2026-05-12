"""
voyager1_position_model.py
--------------------------
Single source of truth for Voyager 1's synthetic heliocentric position.

Per ADR-002 in `deep_space_portal/docs/facts-dynamic-ticket.md`: every page in
the portal that quotes a Voyager 1 distance must route through this module so
`/facts`, `/trajectory`, and analytical scripts can never disagree.

Validation cadence (annual reconciliation against JPL Horizons) updates the
constants in this file — and only this file.

References
----------
- Heliopause crossing: 2012-08-25 at ~121 AU (NASA/JPL announcement).
- Post-heliopause heliocentric outbound rate: ~3.6 AU/yr.
- 1 AU = 149_597_870.7 km (IAU 2012).
- Speed of light in vacuum: light traverses 1 AU in ~499.004784 s.
"""

from __future__ import annotations

import datetime as _dt

# ---------------------------------------------------------------------------
# Physical / unit constants
# ---------------------------------------------------------------------------
AU_KM: float = 149_597_870.7
KM_MILES: float = 0.621371
LIGHT_SECONDS_PER_AU: float = 499.004784

# ---------------------------------------------------------------------------
# Voyager 1 mission constants
# ---------------------------------------------------------------------------
VOYAGER1_LAUNCH: _dt.date = _dt.date(1977, 9, 5)

# Anchor point: heliopause crossing (well-known mission milestone, NASA-confirmed).
# Distances after this anchor are extrapolated linearly at RATE_AU_PER_YR.
HELIOPAUSE_DATE: _dt.date = _dt.date(2012, 8, 25)
HELIOPAUSE_AU: float = 121.0
RATE_AU_PER_YR: float = 3.6

# Pointing direction (J2000): roughly toward the constellation Ophiuchus.
# Used by trajectory visualisations; not needed for scalar distance.
DIRECTION_RA_HOURS: float = 17.22
DIRECTION_DEC_DEGREES: float = 12.08


def voyager1_distance_au(today: _dt.date | None = None) -> float:
    """Synthetic heliocentric distance of Voyager 1, in AU.

    Linear extrapolation from the heliopause crossing anchor. Pure arithmetic,
    no I/O. See module docstring and ADR-002 for rationale.
    """
    if today is None:
        today = _dt.datetime.now(_dt.timezone.utc).date()
    years_since_anchor = (today - HELIOPAUSE_DATE).days / 365.25
    if years_since_anchor < 0:
        # Date before heliopause crossing — caller almost certainly wants the
        # anchor value rather than a negative extrapolation.
        return HELIOPAUSE_AU
    return HELIOPAUSE_AU + years_since_anchor * RATE_AU_PER_YR
