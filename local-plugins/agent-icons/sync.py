#!/usr/bin/env python3
"""Report static agent glyphs as Herdr sidebar metadata."""

from __future__ import annotations

import json
import os
import subprocess
import sys

# Single-cell Unicode symbols: no patched/Nerd Font is required in Ghostty.
ICONS = {
    "claude": "✻",
    "codex": "◉",
    "pi": "π",
    "opencode": "◆",
}
SOURCE = "config.agent-icons"


def herdr(*args: str, capture: bool = False) -> subprocess.CompletedProcess[str]:
    executable = os.environ.get("HERDR_BIN_PATH", "herdr")
    return subprocess.run(
        [executable, *args],
        check=False,
        text=True,
        stdout=subprocess.PIPE if capture else subprocess.DEVNULL,
        stderr=subprocess.PIPE,
    )


def main() -> int:
    listed = herdr("agent", "list", capture=True)
    if listed.returncode != 0:
        print(listed.stderr.rstrip(), file=sys.stderr)
        return listed.returncode

    try:
        agents = json.loads(listed.stdout)["result"]["agents"]
    except (json.JSONDecodeError, KeyError, TypeError) as error:
        print(f"could not parse `herdr agent list`: {error}", file=sys.stderr)
        return 1

    failed = False
    for agent in agents:
        icon = ICONS.get(agent.get("agent"))
        pane_id = agent.get("pane_id")
        if not icon or not pane_id:
            continue
        reported = herdr(
            "pane",
            "report-metadata",
            pane_id,
            "--source",
            SOURCE,
            "--token",
            f"icon={icon}",
        )
        if reported.returncode != 0:
            failed = True
            print(
                f"could not report icon for {agent.get('agent')} in {pane_id}: "
                f"{reported.stderr.rstrip()}",
                file=sys.stderr,
            )

    return int(failed)


if __name__ == "__main__":
    raise SystemExit(main())
