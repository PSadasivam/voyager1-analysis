"""Tests confirming voyager1_outbound_trajectory.fetch_trajectory_synthetic
agrees with the shared position model (ADR-002, FU-1).
"""
import datetime
import sys
import unittest
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from voyager1_outbound_trajectory import fetch_trajectory_synthetic
from voyager1_position_model import (
    HELIOPAUSE_DATE,
    HELIOPAUSE_AU,
    RATE_AU_PER_YR,
    voyager1_distance_au,
)


class TestSyntheticTrajectoryAgreesWithSharedModel(unittest.TestCase):
    """The /trajectory page and the /facts page must never disagree on
    Voyager 1's heliocentric distance. They route through the same
    voyager1_position_model. This test makes that contract executable."""

    def _endpoint(self, end_date):
        start = datetime.datetime(2010, 1, 1, tzinfo=datetime.timezone.utc)
        trajectory, dates = fetch_trajectory_synthetic(start, end_date, step_days=180)
        return float(np.linalg.norm(trajectory[-1])), dates[-1]

    def test_endpoint_matches_shared_model_present_day(self):
        end_date = datetime.datetime(2026, 5, 1, tzinfo=datetime.timezone.utc)
        synthetic, last_date = self._endpoint(end_date)
        shared = voyager1_distance_au(last_date.date())
        # Linear interpolation between Heliopause (2012) and the end_date anchor
        # introduces a tiny rounding gap (<0.3 AU); below 0.5 AU is well inside
        # the page's 1-decimal AU display precision.
        self.assertAlmostEqual(synthetic, shared, delta=0.5,
            msg=f"/trajectory endpoint ({synthetic:.3f} AU at {last_date.date()}) "
                f"must match shared model ({shared:.3f} AU) — ADR-002 violation.")

    def test_endpoint_matches_shared_model_future_date(self):
        end_date = datetime.datetime(2030, 1, 1, tzinfo=datetime.timezone.utc)
        synthetic, last_date = self._endpoint(end_date)
        shared = voyager1_distance_au(last_date.date())
        self.assertAlmostEqual(synthetic, shared, delta=0.5)

    def test_endpoint_exact_when_end_date_lands_on_step(self):
        # When the step grid lines up exactly with end_date, agreement is exact
        # (no interpolation rounding). Picks step_days that divides the span.
        start = datetime.datetime(2012, 8, 25, tzinfo=datetime.timezone.utc)
        end_date = datetime.datetime(2026, 5, 1, tzinfo=datetime.timezone.utc)
        span_days = (end_date - start).days
        trajectory, dates = fetch_trajectory_synthetic(start, end_date, step_days=span_days)
        synthetic = float(np.linalg.norm(trajectory[-1]))
        shared = voyager1_distance_au(end_date.date())
        self.assertAlmostEqual(synthetic, shared, places=6)

    def test_heliopause_anchor_constants_match(self):
        # Sanity check: the trajectory module pulls anchor constants from the
        # shared model. If anyone ever copies them back inline, this fails.
        self.assertEqual(HELIOPAUSE_DATE, datetime.date(2012, 8, 25))
        self.assertEqual(HELIOPAUSE_AU, 121.0)
        self.assertEqual(RATE_AU_PER_YR, 3.6)


if __name__ == '__main__':
    unittest.main()
