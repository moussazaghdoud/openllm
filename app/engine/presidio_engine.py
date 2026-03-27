"""Wave 2 — Personal data anonymization via Presidio.

Adapted from openclaw/presidio/app.py.  Detects and replaces personal
information (names, emails, phones, etc.) with <ENTITY_TYPE_N> placeholders.

Runs in-process (no external service required) but can optionally delegate
to an external Presidio URL for horizontal scaling.
"""

from __future__ import annotations

import httpx
import logging
from presidio_analyzer import AnalyzerEngine
from presidio_analyzer.nlp_engine import NlpEngineProvider
from presidio_anonymizer import AnonymizerEngine

ENTITY_TYPES = [
    "PERSON", "EMAIL_ADDRESS", "PHONE_NUMBER", "CREDIT_CARD",
    "IBAN_CODE", "IP_ADDRESS", "LOCATION", "DATE_TIME",
    "NRP", "MEDICAL_LICENSE", "URL", "ORGANIZATION",
]

# spaCy ORG entities are not natively supported by Presidio,
# so we add a custom recognizer for organizations.
from presidio_analyzer import EntityRecognizer, RecognizerResult


class SpacyOrgRecognizer(EntityRecognizer):
    """Recognizer that leverages spaCy NER to detect ORG entities."""

    ENTITIES = ["ORGANIZATION"]

    def __init__(self):
        super().__init__(
            supported_entities=["ORGANIZATION"],
            supported_language="en",
            name="SpacyOrgRecognizer",
        )

    def load(self):
        pass  # No model to load — we use spaCy's NER via nlp_artifacts

    def analyze(self, text, entities, nlp_artifacts=None, regex_flags=None):
        results = []
        if nlp_artifacts and nlp_artifacts.entities:
            for ent in nlp_artifacts.entities:
                if ent.label_ == "ORG":
                    results.append(
                        RecognizerResult(
                            entity_type="ORGANIZATION",
                            start=ent.start_char,
                            end=ent.end_char,
                            score=0.85,
                        )
                    )
        return results

# Lazy-initialized singletons (heavy on first load due to NLP models)
_analyzer: AnalyzerEngine | None = None
_anonymizer: AnonymizerEngine | None = None


def _get_engines() -> tuple[AnalyzerEngine, AnonymizerEngine]:
    global _analyzer, _anonymizer
    if _analyzer is None:
        # Use whichever spaCy model is installed (sm, md, or lg)
        import spacy.util
        available = [m for m in ["en_core_web_lg", "en_core_web_md", "en_core_web_sm"]
                     if spacy.util.is_package(m)]
        model_name = available[0] if available else "en_core_web_sm"
        provider = NlpEngineProvider(nlp_configuration={
            "nlp_engine_name": "spacy",
            "models": [{"lang_code": "en", "model_name": model_name}],
        })
        _analyzer = AnalyzerEngine(nlp_engine=provider.create_engine())
        _analyzer.registry.add_recognizer(SpacyOrgRecognizer())
        # Silence noisy NER warnings for unmapped entity types
        logging.getLogger("presidio-analyzer").setLevel(logging.ERROR)
        _anonymizer = AnonymizerEngine()
    return _analyzer, _anonymizer  # type: ignore[return-value]


def anonymize(text: str, language: str = "en") -> tuple[str, dict[str, str]]:
    """Detect PII and replace with numbered placeholders.

    Returns (anonymized_text, mapping).
    """
    analyzer, _ = _get_engines()
    results = analyzer.analyze(text=text, entities=ENTITY_TYPES, language=language)
    results = sorted(results, key=lambda r: r.start)

    counters: dict[str, int] = {}
    mapping: dict[str, str] = {}
    placeholder_map: list[tuple[int, int, str]] = []

    for r in results:
        original = text[r.start:r.end]
        # Reuse placeholder if same original already seen
        existing = next((ph for ph, orig in mapping.items() if orig == original), None)
        if existing:
            placeholder_map.append((r.start, r.end, existing))
        else:
            etype = r.entity_type
            counters[etype] = counters.get(etype, 0) + 1
            placeholder = f"<{etype}_{counters[etype]}>"
            mapping[placeholder] = original
            placeholder_map.append((r.start, r.end, placeholder))

    # Replace from end to preserve offsets
    anonymized = text
    for start, end, placeholder in reversed(placeholder_map):
        anonymized = anonymized[:start] + placeholder + anonymized[end:]

    return anonymized, mapping


def deanonymize(text: str, mapping: dict[str, str]) -> str:
    """Restore placeholders to original values."""
    if not mapping:
        return text
    result = text
    for placeholder in sorted(mapping.keys(), key=len, reverse=True):
        result = result.replace(placeholder, mapping[placeholder])
    return result


async def anonymize_via_external(
    url: str, text: str, timeout: float = 10.0
) -> tuple[str, dict[str, str]]:
    """Delegate to an external Presidio service (optional scaling path)."""
    async with httpx.AsyncClient(timeout=timeout) as client:
        resp = await client.post(f"{url.rstrip('/')}/anonymize", json={"text": text})
        resp.raise_for_status()
        data = resp.json()
        return data["anonymized_text"], data.get("mapping", {})


async def deanonymize_via_external(
    url: str, text: str, mapping: dict[str, str], timeout: float = 10.0
) -> str:
    """Delegate deanonymization to an external Presidio service."""
    async with httpx.AsyncClient(timeout=timeout) as client:
        resp = await client.post(
            f"{url.rstrip('/')}/deanonymize",
            json={"text": text, "mapping": mapping},
        )
        resp.raise_for_status()
        return resp.json()["text"]
