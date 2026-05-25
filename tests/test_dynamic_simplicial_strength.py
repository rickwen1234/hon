from __future__ import annotations

import os
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SRC = os.path.join(ROOT, "src")
if SRC not in sys.path:
    sys.path.insert(0, SRC)

from network_science_project.multilayer.strength import (
    InterlayerStrengthConfig,
    StrengthConfig,
    StrengthEvent,
    StrengthState,
    assign_interlayer_strengths,
    impacted_simplices,
)


class DynamicSimplicialStrengthTests(unittest.TestCase):
    def test_closure_scope_uses_dimension_discount(self) -> None:
        impacted = dict(impacted_simplices(("a", "b", "c"), scope="closure", rho=0.5))

        self.assertAlmostEqual(impacted[("a", "b", "c")], 1.0)
        self.assertAlmostEqual(impacted[("a", "b")], 0.5)
        self.assertAlmostEqual(impacted[("a",)], 0.25)

    def test_positive_and_negative_events_share_scope(self) -> None:
        state = StrengthState(StrengthConfig(mu=0.8, eta=0.5, event_scope="closure", rho=0.5))

        state.apply_event(StrengthEvent(("a", "b", "c"), time=1.0, signal=1.0))
        self.assertAlmostEqual(state.get_strength(("a", "b", "c")), 0.8)
        self.assertAlmostEqual(state.get_strength(("a", "b")), 0.4)
        self.assertAlmostEqual(state.get_strength(("a",)), 0.2)

        state.apply_event(StrengthEvent(("a", "b", "c"), time=2.0, signal=-1.0))
        self.assertAlmostEqual(state.get_strength(("a", "b", "c")), 0.4)
        self.assertAlmostEqual(state.get_strength(("a", "b")), 0.3)
        self.assertAlmostEqual(state.get_strength(("a",)), 0.175)

    def test_inactive_simplex_can_recover(self) -> None:
        state = StrengthState(StrengthConfig(mu=0.6, eta=1.0, theta_active=0.2, event_scope="exact"))

        state.apply_event(StrengthEvent(("a", "b"), time=1.0, signal=1.0))
        self.assertTrue(state.is_active(("a", "b")))
        state.apply_event(StrengthEvent(("a", "b"), time=2.0, signal=-1.0))
        self.assertFalse(state.is_active(("a", "b")))
        state.apply_event(StrengthEvent(("a", "b"), time=3.0, signal=1.0))
        self.assertTrue(state.is_active(("a", "b")))

    def test_interlayer_strength_schemes(self) -> None:
        deps = [("a1", "b1"), ("a2", "b2")]

        constant = assign_interlayer_strengths(deps, InterlayerStrengthConfig(scheme="peng_constant", q_global=0.7))
        self.assertEqual(constant, [("a1", "b1", 0.7), ("a2", "b2", 0.7)])

        fixed = assign_interlayer_strengths(
            [("a1", "b1", 0.3), ("a2", "b2", 1.4)],
            InterlayerStrengthConfig(scheme="fixed_strength"),
        )
        self.assertEqual(fixed, [("a1", "b1", 0.3), ("a2", "b2", 1.0)])

        random_strengths = assign_interlayer_strengths(
            deps,
            InterlayerStrengthConfig(scheme="random_strength", q_global=0.5, sigma=0.0, seed=1),
        )
        self.assertEqual(random_strengths, [("a1", "b1", 0.5), ("a2", "b2", 0.5)])


if __name__ == "__main__":
    unittest.main()
