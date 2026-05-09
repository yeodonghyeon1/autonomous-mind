import os
from pathlib import Path

import anthropic

_PROMPTS_DIR = Path(__file__).parent.parent / "prompts"


def _load_prompt(name: str) -> str:
    return (_PROMPTS_DIR / f"{name}.md").read_text(encoding="utf-8")


def _call(system: str, user_message: str, model: str, max_tokens: int) -> str:
    client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
    response = client.messages.create(
        model=model,
        max_tokens=max_tokens,
        system=system,
        messages=[{"role": "user", "content": user_message}],
    )
    return response.content[0].text


def brain_generate(domain_context: str, state: dict, model: str, max_tokens: int) -> str:
    user_msg = f"""## Domain Context
{domain_context}

## Current State
- Cycle: {state['cycle']}
- Previous Hypothesis: {state.get('last_hypothesis') or 'None (first cycle)'}
- Next Hypothesis Seed: {state.get('next_hypothesis_seed') or 'Start from scratch'}
- Accumulated Insights: {chr(10).join(f"- {i}" for i in state.get('key_insights', [])) or 'None yet'}

You are in **Mode A — Hypothesis Generation**. Generate the hypothesis for cycle {state['cycle']}."""
    return _call(_load_prompt("brain"), user_msg, model, max_tokens)


def curiosity_explore(domain_context: str, hypothesis: str, model: str, max_tokens: int) -> str:
    user_msg = f"""## Domain Context
{domain_context}

## Current Hypothesis
{hypothesis}

Explore this hypothesis. Seek prediction error. Find what surprises you."""
    return _call(_load_prompt("curiosity"), user_msg, model, max_tokens)


def compulsion_verify(domain_context: str, hypothesis: str, model: str, max_tokens: int) -> str:
    user_msg = f"""## Domain Context
{domain_context}

## Current Hypothesis
{hypothesis}

Verify this hypothesis. Seek convergent evidence. Confirm the prediction."""
    return _call(_load_prompt("compulsion"), user_msg, model, max_tokens)


def brain_synthesize(
    domain_context: str,
    hypothesis: str,
    curiosity_result: str,
    compulsion_result: str,
    state: dict,
    model: str,
    max_tokens: int,
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
    return _call(_load_prompt("brain"), user_msg, model, max_tokens)
