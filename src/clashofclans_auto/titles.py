"""Decide whether a window title belongs to the game client."""


def is_clash_window_title(title: str) -> bool:
    """Return true when the title is the game window itself."""
    folded = " ".join(title.split()).casefold()
    compact = "".join(folded.split())
    if "clashofclans_auto" in compact:
        return False
    if folded.startswith("clash of clans"):
        return True
    return title.strip().startswith("部落冲突")
