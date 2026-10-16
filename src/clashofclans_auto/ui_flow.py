"""Clickable controls and the operation flow built from them.

A control is one thing the player can press, such as 搜索对手 or 回营.
A screen is the set of controls visible together.
A phase says which controls may be pressed, and which screen ends that phase.
The flow does not store coordinates and does not click.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Control:
    id: str
    label: str


@dataclass(frozen=True)
class Screen:
    id: str
    label: str
    controls: tuple[Control, ...]

    def control_ids(self) -> frozenset[str]:
        return frozenset(control.id for control in self.controls)


@dataclass(frozen=True)
class Phase:
    """Press the allowed controls while one of screens is visible.

    once means press the single named control, then the next screen appears.
    until means those controls may be pressed again until until_screen appears.
    """

    screens: tuple[str, ...]
    controls: tuple[str, ...]
    until_screen: str
    repeat: bool = False


@dataclass(frozen=True)
class Flow:
    id: str
    label: str
    phases: tuple[Phase, ...]


def _screen(screen_id: str, label: str, controls: tuple[tuple[str, str], ...]) -> Screen:
    return Screen(
        screen_id,
        label,
        tuple(Control(control_id, control_label) for control_id, control_label in controls),
    )


SCREENS: dict[str, Screen] = {
    screen.id: screen
    for screen in (
        _screen("home", "家乡", (("battle", "战斗"),)),
        _screen(
            "attack_menu",
            "攻击选择",
            (
                ("search", "搜索对手"),
                ("edit_army", "编辑军队"),
            ),
        ),
        _screen(
            "army",
            "军队",
            (
                ("attack", "进攻"),
                ("close", "关闭"),
            ),
        ),
        _screen(
            "battle_prep",
            "战斗准备",
            (
                ("end_battle", "结束战斗"),
                ("next_opponent", "下一个"),
                ("troop_slot", "兵种栏"),
                ("spell_slot", "法术栏"),
                ("map", "战场"),
            ),
        ),
        _screen(
            "battle",
            "战斗中",
            (
                ("surrender", "放弃"),
                ("troop_slot", "兵种栏"),
                ("spell_slot", "法术栏"),
                ("map", "战场"),
            ),
        ),
        _screen("results", "结算", (("return_home", "回营"),)),
    )
}


SINGLE_PLAYER_ATTACK = Flow(
    id="single_player_attack",
    label="单人搜索并完成一场战斗",
    phases=(
        Phase(("home",), ("battle",), "attack_menu"),
        Phase(("attack_menu",), ("search",), "army"),
        Phase(("army",), ("attack",), "battle_prep"),
        Phase(
            ("battle_prep", "battle"),
            ("troop_slot", "spell_slot", "map"),
            "results",
            repeat=True,
        ),
        Phase(("results",), ("return_home",), "home"),
    ),
)


class FlowError(ValueError):
    """The flow names a screen or control that is not defined."""


def validate_flow(flow: Flow, screens: dict[str, Screen] = SCREENS) -> None:
    """Reject a flow that presses a control the current screens do not contain."""
    if not flow.phases:
        raise FlowError(f"{flow.id} has no phases")
    for index, phase in enumerate(flow.phases, start=1):
        if not phase.screens or not phase.controls:
            raise FlowError(f"{flow.id} phase {index} is empty")
        if phase.until_screen not in screens:
            raise FlowError(f"{flow.id} phase {index} ends on unknown screen {phase.until_screen}")
        visible: set[str] = set()
        for screen_id in phase.screens:
            screen = screens.get(screen_id)
            if screen is None:
                raise FlowError(f"{flow.id} phase {index} uses unknown screen {screen_id}")
            if not visible:
                visible.update(screen.control_ids())
            else:
                visible &= screen.control_ids()
        missing = [control_id for control_id in phase.controls if control_id not in visible]
        if missing:
            raise FlowError(
                f"{flow.id} phase {index} presses {', '.join(missing)} "
                f"outside {', '.join(phase.screens)}"
            )
        if not phase.repeat and len(phase.controls) != 1:
            raise FlowError(f"{flow.id} phase {index} must name one control")
