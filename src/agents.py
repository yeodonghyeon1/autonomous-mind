import subprocess
from pathlib import Path

_PROMPTS_DIR = Path(__file__).parent.parent / "prompts"


def _load_prompt(name: str) -> str:
    return (_PROMPTS_DIR / f"{name}.md").read_text(encoding="utf-8")


def _call(system: str, user_message: str, model: str) -> str:
    result = subprocess.run(
        ["claude", "-p", "--system", system, "--model", model],
        input=user_message,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    if result.returncode != 0:
        raise RuntimeError(f"Claude CLI error:\n{result.stderr}")
    return result.stdout.strip()


def brain_generate(domain_context: str, state: dict, model: str) -> str:
    corrections = state.get("last_critique_corrections")
    critique_block = (
        f"\n## Critic's Mandatory Corrections (from last cycle)\n{corrections}"
        if corrections
        else ""
    )
    user_msg = f"""## Domain Context
{domain_context}

## Current State
- Cycle: {state['cycle']}
- Previous Hypothesis: {state.get('last_hypothesis') or 'None (first cycle)'}
- Next Hypothesis Seed: {state.get('next_hypothesis_seed') or 'Start from scratch'}
- Accumulated Insights: {chr(10).join(f"- {i}" for i in state.get('key_insights', [])) or 'None yet'}{critique_block}

You are in **Mode A — Hypothesis Generation**. Generate the hypothesis for cycle {state['cycle']}."""
    return _call(_load_prompt("brain"), user_msg, model)


def curiosity_explore(domain_context: str, hypothesis: str, model: str) -> str:
    user_msg = f"""## Domain Context
{domain_context}

## Current Hypothesis
{hypothesis}

Explore this hypothesis. Seek prediction error. Find what surprises you."""
    return _call(_load_prompt("curiosity"), user_msg, model)


def compulsion_verify(domain_context: str, hypothesis: str, model: str) -> str:
    user_msg = f"""## Domain Context
{domain_context}

## Current Hypothesis
{hypothesis}

Verify this hypothesis. Seek convergent evidence. Confirm the prediction."""
    return _call(_load_prompt("compulsion"), user_msg, model)


def brain_synthesize(
    domain_context: str,
    hypothesis: str,
    curiosity_result: str,
    compulsion_result: str,
    state: dict,
    model: str,
) -> str:
    user_msg = f"""## Domain Context
{domain_context}

## This Cycle's Hypothesis
{hypothesis}

## Curiosity Agent Results
{curiosity_result}

## Compulsion Agent Results
{compulsion_result}

## Accumulated Insights So Far
{chr(10).join(f"- {i}" for i in state.get('key_insights', [])) or 'None yet'}

You are in **Mode B — Synthesis**. Synthesize cycle {state['cycle']} and generate the next hypothesis seed."""
    return _call(_load_prompt("brain"), user_msg, model)


def critic_review(
    hypothesis: str,
    curiosity_result: str,
    compulsion_result: str,
    synthesis: str,
    accumulated_insights: list[str],
    model: str,
) -> str:
    prior = "\n".join(f"- {i}" for i in accumulated_insights) or "None yet"
    user_msg = f"""## Accumulated Insights from Prior Cycles
{prior}

---

## This Cycle — Full Output

### Hypothesis
{hypothesis}

### Curiosity Agent
{curiosity_result}

### Compulsion Agent
{compulsion_result}

### Brain Synthesis
{synthesis}

---

Review the above cycle output. Flag logical errors, duplications, unsupported claims, and internal consistency issues."""
    return _call(_load_prompt("critic"), user_msg, model)
