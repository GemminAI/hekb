"""EXP-HEKB006's per-observer ingestion orchestrator.

A boundary module, mirroring `_multimodal_extractors.py`'s convention
exactly: `_observer_adapter.probe_observer_availability` (a real
environment check) gates whether `run_observer` is even attempted, and
`run_observer` itself always raises `NotImplementedError` naming exactly
what concrete integration -- which package, which API -- would be needed,
because no real, callable access to any of the 7 named engines exists in
this workspace. No fabricated text is ever returned in its place, per the
specification's own "DO NOT fabricate outputs" instruction.

Even were an observer's raw text obtainable, this workspace still has no
real Meaning Mapper to project arbitrary natural language into a
`msr.abi.MeaningMeasurement` -- the same "meaning-mapper doesn't exist"
gap `docs/RFC_ALIGNMENT.md` (EXP-HEKB002-005) already recorded, now
blocking the ingestion side of this pipeline as well as the observation
side. `run_all_observers` reports this real, checked outcome per engine;
it does not silently skip the gap or paper over it with a single
top-level message.
"""

from __future__ import annotations

from dataclasses import dataclass

from _observer_adapter import ObserverAvailability, ObserverName, probe_observer_availability

#: What a real implementation of each engine's `ObserverAdapter` is
#: expected to integrate, recorded here so the boundary is concrete, even
#: though no body is written yet -- the same purpose
#: `_multimodal_extractors.REFERENCE_APPROACH` serves for audio/score/etc.
REFERENCE_APPROACH: dict[ObserverName, str] = {
    "Gemma": "a local `ollama run gemma2` call once `ollama pull gemma2` has been run",
    "Qwen": "a local `ollama run qwen2.5` call once `ollama pull qwen2.5` has been run",
    "Llama": "a local `ollama run llama3.1` call once `ollama pull llama3.1` has been run",
    "Mistral": "a local `ollama run mistral` call once `ollama pull mistral` has been run",
    "Claude": "the Anthropic Messages API (`anthropic` package) via `ANTHROPIC_API_KEY`",
    "GPT": "the OpenAI Chat Completions API (`openai` package) via `OPENAI_API_KEY`",
    "Gemini": (
        "the Gemini API (`google-generativeai` package) authenticated via "
        "`GOOGLE_API_KEY`/`GEMINI_API_KEY`"
    ),
}


def run_observer(name: ObserverName, target_prompt: str, availability: ObserverAvailability) -> str:
    """Always raises: no concrete implementation of `ObserverAdapter`
    exists for any of the 7 named engines in this workspace. `target_prompt`
    is accepted (matching the real `ObserverAdapter.observe` signature a
    future implementation must satisfy) but unused -- there is nothing to
    send it to yet."""
    del target_prompt  # unused: no real call is made; see docstring
    if not availability.available:
        raise NotImplementedError(
            f"{name} is not available in this environment ({availability.reason}); "
            f"no call is attempted. Expected integration once available: "
            f"{REFERENCE_APPROACH[name]}."
        )
    raise NotImplementedError(  # pragma: no cover - unreachable while every probe is unavailable
        f"{name} reports a credential/local model as present ({availability.reason}), but no "
        f"concrete API-calling implementation has been written in this workspace yet -- avoiding "
        f"an unreviewed real network call (with billing/consent implications) rather than "
        f"fabricating one. Expected integration: {REFERENCE_APPROACH[name]}."
    )


@dataclass(frozen=True, slots=True)
class ObserverRunResult:
    """One real, checked outcome for one named engine -- `raw_text` is
    `None` unless a real call actually returned real text (it never does
    in this workspace today; see `succeeded`)."""

    name: ObserverName
    availability: ObserverAvailability
    succeeded: bool
    error: str | None
    raw_text: str | None


def run_all_observers(target_prompt: str) -> tuple[ObserverRunResult, ...]:
    """Attempt every named engine, in specification order, and report a
    real, per-engine outcome -- continuing past every unavailable/failed
    observer rather than stopping at the first one, per the
    specification's own "continue with available observers" instruction."""
    results: list[ObserverRunResult] = []
    for availability in probe_observer_availability():
        try:
            raw_text = run_observer(availability.name, target_prompt, availability)
        except NotImplementedError as exc:
            results.append(
                ObserverRunResult(
                    name=availability.name,
                    availability=availability,
                    succeeded=False,
                    error=str(exc),
                    raw_text=None,
                )
            )
        else:  # pragma: no cover - unreachable while every probe is unavailable
            results.append(
                ObserverRunResult(
                    name=availability.name,
                    availability=availability,
                    succeeded=True,
                    error=None,
                    raw_text=raw_text,
                )
            )
    return tuple(results)


__all__ = ["REFERENCE_APPROACH", "ObserverRunResult", "run_all_observers", "run_observer"]
