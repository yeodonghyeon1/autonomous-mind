"""Main cycle runner. Called once per loop tick."""
import sys
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).parent))

from agents import brain_generate, brain_synthesize, compulsion_verify, critic_review, curiosity_explore
from obsidian import append_critique, update_moc, write_session
from state import extract_section, load_state, save_state

_CONFIG_PATH = Path(__file__).parent.parent / "config" / "system.yaml"
_DOMAIN_PATH = Path(__file__).parent.parent / "config" / "domain.md"


def _load_config() -> dict:
    with open(_CONFIG_PATH, encoding="utf-8") as f:
        return yaml.safe_load(f)


def _load_domain() -> str:
    return _DOMAIN_PATH.read_text(encoding="utf-8")


def run_cycle() -> None:
    config = _load_config()
    domain_context = _load_domain()
    model: str = config["model"]

    state = load_state()
    state["cycle"] += 1
    cycle = state["cycle"]

    print(f"\n[Brain] Cycle {cycle} — generating hypothesis...")
    hypothesis = brain_generate(domain_context, state, model)
    print(hypothesis)

    print("\n[Curiosity] Exploring...")
    curiosity_result = curiosity_explore(domain_context, hypothesis, model)
    print(curiosity_result)

    print("\n[Compulsion] Verifying...")
    compulsion_result = compulsion_verify(domain_context, hypothesis, model)
    print(compulsion_result)

    print("\n[Brain] Synthesizing...")
    synthesis = brain_synthesize(
        domain_context, hypothesis, curiosity_result, compulsion_result, state, model
    )
    print(synthesis)

    session_path = write_session(cycle, hypothesis, curiosity_result, compulsion_result, synthesis)

    state["last_hypothesis"] = extract_section(hypothesis, "## Hypothesis")
    state["next_hypothesis_seed"] = extract_section(synthesis, "## Next Hypothesis Seed")

    new_insights = [
        line.lstrip("- ").strip()
        for line in extract_section(synthesis, "## Key Insights").splitlines()
        if line.strip().startswith("-")
    ]
    existing = state.get("key_insights", [])
    state["key_insights"] = (existing + new_insights)[-30:]

    print("\n[Critic] Reviewing session...")
    critique = critic_review(
        hypothesis, curiosity_result, compulsion_result, synthesis,
        state["key_insights"], model,
    )
    print(critique)

    append_critique(session_path, critique)

    corrections = extract_section(critique, "## Mandatory Corrections for Next Cycle")
    state["last_critique_corrections"] = corrections if corrections != "None." else None

    update_moc(cycle, session_path, synthesis)
    save_state(state)
    print(f"\n✓ Cycle {cycle} saved → {session_path.name}")


if __name__ == "__main__":
    run_cycle()
