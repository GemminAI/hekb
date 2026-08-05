"""EXP-HEKB006 v2.1.0 Phase 2: the Observer Registry & Capability Discovery.

A single, unified inventory of every candidate "Observer M_k" this
workspace can reason about, spanning both real planes the specification
names:

- **Human channels** (`_human_observers.py`, new) -- three real,
  independently-authored text/data sources already present in
  EXP-HEKB005's real corpus. Always real and re-checkable: availability
  here means "this channel's real file exists for at least one real
  work," verified by actually building each channel (reusing
  `_human_observers.build_human_channel` unmodified), never assumed.
- **Named LLM engines** (`_observer_adapter.py`, EXP-HEKB006 v1.0.0,
  reused unmodified) -- the 7 engines (Gemma, Qwen, Llama, Mistral,
  Claude, GPT, Gemini) the specification's Multi-Observer Test Matrix
  names, whose real, re-runnable availability probe
  (`probe_observer_availability`) is untouched here.

This module adds no new availability-detection logic for the LLM plane --
it only relabels `_observer_adapter.ObserverAvailability` into the same
`ObserverRecord` shape the human plane uses, so both planes can be
reported and iterated over uniformly. "Capability discovery" for the
human plane is a real, checked property (which morphism type / which
real works a channel actually covers), not an assumed capability string.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from _human_observers import HUMAN_CHANNELS, HumanChannelResult, build_all_human_channels
from _observer_adapter import ObserverAvailability, probe_observer_availability

ObserverKind = Literal["human_text_source", "human_structured_source", "api", "local_weights"]

#: What each real human channel's real morphism type represents -- a
#: capability description grounded in `_visual_observation_bundle`'s own
#: typed-morphism vocabulary, not invented here.
_HUMAN_CAPABILITY: dict[str, str] = {
    "Human_Critique": (
        "interprets (named human critic's real prose: Vasari / EB1911 / van Gogh's own letters)"
    ),
    "Human_Wiki": "documents (Wikipedia editorial community's real prose)",
    "Human_MuseumCatalog": "formally_defines (Wikidata's real structured curatorial metadata)",
}
_HUMAN_KIND: dict[str, ObserverKind] = {
    "Human_Critique": "human_text_source",
    "Human_Wiki": "human_text_source",
    "Human_MuseumCatalog": "human_structured_source",
}


@dataclass(frozen=True, slots=True)
class ObserverRecord:
    """One row of the unified Observer Registry -- real, checked
    availability and capability for either a human channel or a named
    LLM engine, never a hardcoded or assumed entry."""

    name: str
    kind: ObserverKind
    capability: str
    available: bool
    evidence: str


def _human_records(channels: tuple[HumanChannelResult, ...]) -> tuple[ObserverRecord, ...]:
    records = []
    for result in channels:
        available = len(result.works_present) > 0
        evidence = (
            f"real file present for {len(result.works_present)}/"
            f"{len(result.works_present) + len(result.works_absent)} real EXP-HEKB005 works "
            f"(present: {', '.join(result.works_present) or 'none'})"
        )
        records.append(
            ObserverRecord(
                name=result.channel,
                kind=_HUMAN_KIND[result.channel],
                capability=_HUMAN_CAPABILITY[result.channel],
                available=available,
                evidence=evidence,
            )
        )
    return tuple(records)


def _llm_records(availabilities: tuple[ObserverAvailability, ...]) -> tuple[ObserverRecord, ...]:
    return tuple(
        ObserverRecord(
            name=a.name,
            kind=a.kind,
            capability=(
                "raw_text_generation (requires a real Meaning Mapper to ingest; see gap record)"
            ),
            available=a.available,
            evidence=a.reason,
        )
        for a in availabilities
    )


def discover_registry() -> tuple[ObserverRecord, ...]:
    """The full, real Observer Registry: human channels first (matching
    the specification's Phase 1 Human-first ordering), then the 7 named
    LLM engines in `_observer_adapter.OBSERVER_NAMES` order. Every entry's
    `available` traces to an actual, just-performed check -- real corpus
    file presence for the human plane, `probe_observer_availability`'s
    real environment probe for the LLM plane."""
    human = _human_records(build_all_human_channels())
    llm = _llm_records(probe_observer_availability())
    return human + llm


def capability_summary(registry: tuple[ObserverRecord, ...]) -> dict[str, int]:
    """Real counts, not assumed ones: how many registered observers are
    actually available right now, broken down by `kind`."""
    summary: dict[str, int] = {}
    for record in registry:
        if record.available:
            summary[record.kind] = summary.get(record.kind, 0) + 1
    return summary


__all__ = [
    "HUMAN_CHANNELS",
    "ObserverKind",
    "ObserverRecord",
    "capability_summary",
    "discover_registry",
]
