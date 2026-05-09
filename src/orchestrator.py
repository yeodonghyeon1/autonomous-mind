"""Main cycle runner. Called once per loop tick."""
import sys
from pathlib import Path

import yaml
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent.parent / ".env")

sys.path.insert(0, str(Path(__file__).parent))

from agents import brain_generate, brain_synthesize, compulsion_verify, curiosity_explore
from obsidian import update_moc, write_session
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
    max_tokens: int = config.get("max_tokens", 3000)

    state = load_state()
    state["cycle"] += 1
    cycle = state["cycle"]

    print(f"\n[Brain] Cycle {cycle} — generating hypothesis...")
    hypothesis = brain_generate(domain_context, state, model, max_tokens)
    print(hypothesis)

    print("\n[Curiosity] Exploring...")
    curiosity_result = curiosity_explore(domain_context, hypothesis, model, max_tokens)
    print(curiosity_result)

    print("\n[Compulsion] Verifying...")
    compulsion_result = compulsion_verify(domain_context, hypothesis, model, max_tokens)
    print(compulsion_result)

    print("\n[Brain] Synthesizing...")
    synthesis = brain_synthesize(
        domain_context, hypothesis, curiosity_result, compulsion_result, state, model, max_tokens
    )
    print(synthesis)

    session_path = write_session(cycle, hypothesis, curiosity_result, compulsion_result, synthesis)
    update_moc(cycle, session_path, synthesis)

    state["last_hypothesis"] = extract_section(hypothesis, "## Hypothesis")
    state["next_hypothesis_seed"] = extract_section(synthesis, "## Next Hypothesis Seed")

    new_insights = [
        line.lstrip("- ").strip()
        for line in extract_section(synthesis, "## Key Insights").splitlines()
        if line.strip().startswith("-")
    ]
    existing = state.get("key_insights", [])
    state["key_insights"] = (existing + new_insights)[-30:]  # keep last 30 insights

    save_state(state)
    print(f"\n✓ Cycle {cycle} saved → {session_path.name}")


if __name__ == "__main__":
    run_cycle()
