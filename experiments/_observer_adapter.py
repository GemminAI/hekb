"""EXP-HEKB006's Observer (LLM) adapter boundary.

The specification's "Multi-LLM Observer Matrix" names 7 engines (Gemma,
Qwen, Llama, Mistral, Claude, GPT, Gemini) as the Observer M_k step in the
pipeline Observer -> Meaning Mapper -> MSR -> CLE -> HEKB -> Semantic
Closure. This module is the extractor-style *boundary* for that step only
-- exactly `_multimodal_extractors.py`'s convention (a `Protocol` for what
a real integration must satisfy, plus a real, runtime check of what this
environment actually has, never an assumed or hardcoded result).

`probe_observer_availability` is a real check, in the same spirit as
`_multimodal_corpus.discover_corpus` scanning a real directory: it looks
for an actual local model runtime (`ollama` on `PATH`, or an importable
`llama_cpp`/`transformers` package) for the four open-weights engines, and
an actual API credential (a named environment variable) for the three
proprietary engines. Re-running this function after e.g. `ollama pull
gemma2` or `export ANTHROPIC_API_KEY=...` would honestly reflect the
change without any code here being edited -- nothing about the result is
fixed in advance.

As of this experiment's implementation (see
`experiments/EXP-HEKB006/specification.md`, "Implementation Status"), a
real check in this workspace found zero of the 7 named engines available:
no local model runtime and no API credential for any of them. Per the
specification's own "DO NOT fabricate outputs ... mark the observer
unavailable" instruction, no text is invented in their place anywhere in
this module or its callers (see `_cross_model_runner.py`).
"""

from __future__ import annotations

import importlib.util
import os
import shutil
import subprocess
from dataclasses import dataclass
from typing import Literal, Protocol, runtime_checkable

ObserverName = Literal["Gemma", "Qwen", "Llama", "Mistral", "Claude", "GPT", "Gemini"]

#: Specification section II's Multi-LLM Observer Matrix order.
OBSERVER_NAMES: tuple[ObserverName, ...] = (
    "Gemma",
    "Qwen",
    "Llama",
    "Mistral",
    "Claude",
    "GPT",
    "Gemini",
)

LOCAL_ENGINES: tuple[ObserverName, ...] = ("Gemma", "Qwen", "Llama", "Mistral")

#: Real environment variable names each proprietary engine's official SDK
#: reads its credential from -- not this module's own invention.
API_ENV_VARS: dict[ObserverName, tuple[str, ...]] = {
    "Claude": ("ANTHROPIC_API_KEY",),
    "GPT": ("OPENAI_API_KEY",),
    "Gemini": ("GOOGLE_API_KEY", "GEMINI_API_KEY"),
}

_OLLAMA_LIST_TIMEOUT_S = 5.0


@runtime_checkable
class ObserverAdapter(Protocol):
    """The shape a real per-model observer must satisfy: given a prompt
    describing a real Target Object Q, return that model's real raw text
    description of it. No implementation of this Protocol exists anywhere
    in this workspace for any of the 7 named engines -- see
    `probe_observer_availability` for exactly why, per engine."""

    def observe(self, target_prompt: str) -> str: ...


@dataclass(frozen=True, slots=True)
class ObserverAvailability:
    """One real, checked availability result for one named engine.
    `available=True` means a credential or a matching local model was
    actually found -- never an assumption. See `reason` for exactly what
    was checked and what it found."""

    name: ObserverName
    kind: Literal["local_weights", "api"]
    available: bool
    reason: str


def _api_credential_present(*env_vars: str) -> str | None:
    for var in env_vars:
        if os.environ.get(var):
            return var
    return None


def _ollama_models() -> tuple[str, ...] | None:
    """Real `ollama list` output, lowercased model names -- `None` if the
    `ollama` binary is not on `PATH` or the call fails for any reason
    (missing daemon, etc.); never an assumed model list."""
    if shutil.which("ollama") is None:
        return None
    try:
        completed = subprocess.run(
            ["ollama", "list"],
            capture_output=True,
            text=True,
            timeout=_OLLAMA_LIST_TIMEOUT_S,
            check=False,
        )
    except (OSError, subprocess.SubprocessError):
        return None
    if completed.returncode != 0:
        return None
    return tuple(line.lower() for line in completed.stdout.splitlines())


def _local_engine_availability(
    name: ObserverName, ollama_models: tuple[str, ...] | None
) -> ObserverAvailability:
    if importlib.util.find_spec("llama_cpp") is not None:
        return ObserverAvailability(
            name=name,
            kind="local_weights",
            available=False,
            reason=(
                "`llama_cpp` package is importable, but no model-selection "
                "convention exists in this workspace to identify which local "
                "GGUF file corresponds to this engine -- treating as "
                "unavailable rather than guessing a model path"
            ),
        )
    if ollama_models is None:
        return ObserverAvailability(
            name=name,
            kind="local_weights",
            available=False,
            reason=(
                "no local model runtime found (`ollama` not on PATH; `llama_cpp` not importable)"
            ),
        )
    matched = tuple(line for line in ollama_models if name.lower() in line)
    if matched:
        return ObserverAvailability(
            name=name,
            kind="local_weights",
            available=True,
            reason=f"`ollama list` shows a matching pulled model: {matched[0]!r}",
        )
    return ObserverAvailability(
        name=name,
        kind="local_weights",
        available=False,
        reason=(
            "`ollama` is installed, but `ollama list` shows no pulled model matching this engine"
        ),
    )


def probe_observer_availability() -> tuple[ObserverAvailability, ...]:
    """A real, runtime check of all 7 named engines, in specification
    order. Every result traces to an actual check performed just now --
    `shutil.which`, `importlib.util.find_spec`, a real `ollama list`
    subprocess call, or `os.environ.get` -- never a hardcoded outcome."""
    ollama_models = _ollama_models()
    results: list[ObserverAvailability] = []
    for name in OBSERVER_NAMES:
        if name in LOCAL_ENGINES:
            results.append(_local_engine_availability(name, ollama_models))
        else:
            env_vars = API_ENV_VARS[name]
            found = _api_credential_present(*env_vars)
            results.append(
                ObserverAvailability(
                    name=name,
                    kind="api",
                    available=found is not None,
                    reason=(
                        f"credential found in ${found}"
                        if found is not None
                        else f"no API credential found (checked: {', '.join(env_vars)})"
                    ),
                )
            )
    return tuple(results)


__all__ = [
    "API_ENV_VARS",
    "LOCAL_ENGINES",
    "OBSERVER_NAMES",
    "ObserverAdapter",
    "ObserverAvailability",
    "ObserverName",
    "probe_observer_availability",
]
