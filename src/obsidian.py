from datetime import datetime
from pathlib import Path

_VAULT = Path(__file__).parent.parent / "vault"


def write_session(
    cycle: int,
    hypothesis: str,
    curiosity_result: str,
    compulsion_result: str,
    synthesis: str,
) -> Path:
    sessions_dir = _VAULT / "sessions"
    sessions_dir.mkdir(parents=True, exist_ok=True)

    now = datetime.now()
    timestamp = now.strftime("%Y-%m-%d_%H-%M")
    path = sessions_dir / f"cycle-{cycle:04d}_{timestamp}.md"

    content = f"""---
cycle: {cycle}
date: {now.strftime("%Y-%m-%d")}
time: {now.strftime("%H:%M")}
tags: [cycle-{cycle}, session]
---

# Cycle {cycle} — {timestamp}

## Hypothesis
{hypothesis}

---

## Curiosity Agent
{curiosity_result}

---

## Compulsion Agent
{compulsion_result}

---

## Brain Synthesis
{synthesis}
"""
    path.write_text(content, encoding="utf-8")
    return path


def update_moc(cycle: int, session_path: Path, synthesis_snippet: str) -> None:
    moc_path = _VAULT / "MOC.md"
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    entry = f"- [[sessions/{session_path.stem}]] — Cycle {cycle:04d} ({now})\n"

    if not moc_path.exists():
        moc_path.write_text(
            "# Map of Content\n\n## Sessions\n\n",
            encoding="utf-8",
        )

    content = moc_path.read_text(encoding="utf-8")

    if "## Sessions" in content:
        content = content.replace("## Sessions\n", f"## Sessions\n{entry}", 1)
    else:
        content += f"\n## Sessions\n{entry}"

    moc_path.write_text(content, encoding="utf-8")
