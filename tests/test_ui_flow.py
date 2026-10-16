"""The attack flow only presses controls that belong to the current screen."""

import unittest

from clashofclans_auto.ui_flow import (
    SINGLE_PLAYER_ATTACK,
    Flow,
    FlowError,
    Phase,
    validate_flow,
)


class AttackFlowTests(unittest.TestCase):
    def test_recorded_attack_is_a_closed_sequence(self) -> None:
        validate_flow(SINGLE_PLAYER_ATTACK)
        phases = SINGLE_PLAYER_ATTACK.phases
        self.assertEqual(
            [phase.until_screen for phase in phases],
            ["attack_menu", "army", "battle_prep", "results", "home"],
        )
        self.assertEqual(phases[0].controls, ("battle",))
        self.assertEqual(phases[1].controls, ("search",))
        self.assertEqual(phases[2].controls, ("attack",))
        self.assertEqual(phases[3].controls, ("troop_slot", "spell_slot", "map"))
        self.assertTrue(phases[3].repeat)
        self.assertEqual(phases[4].controls, ("return_home",))

    def test_a_control_from_another_screen_is_rejected(self) -> None:
        flow = Flow(
            "bad",
            "错误流程",
            (Phase(("home",), ("return_home",), "results"),),
        )
        with self.assertRaises(FlowError):
            validate_flow(flow)

    def test_a_one_step_phase_cannot_list_several_controls(self) -> None:
        flow = Flow(
            "bad",
            "错误流程",
            (Phase(("battle_prep",), ("end_battle", "next_opponent"), "results"),),
        )
        with self.assertRaises(FlowError):
            validate_flow(flow)


if __name__ == "__main__":
    unittest.main()
