"""Two-wave anonymization pipeline — the core of SecureLLM.

Wave 1: PPI (Proprietary/Product Information) — customer-specific terms
Wave 2: PII (Personal Identifiable Information) — Presidio detection

ALL data MUST pass through this pipeline before reaching any LLM.
This module is the single enforcement point — no bypass is allowed.
"""

from __future__ import annotations

import json
import logging
import uuid

import redis.asyncio as aioredis

from app.config import settings
from app.engine.ppi import PPIAnonymizer, DEFAULT_PPI_TERMS
from app.engine import presidio_engine

logger = logging.getLogger("securellm.pipeline")

# Mapping TTL: 7 days (same as openclaw)
MAPPING_TTL = 86400 * 7


class PrivacyPipeline:
    """Per-workspace anonymization pipeline.

    Usage:
        pipeline = await PrivacyPipeline.for_workspace(redis, workspace_id)
        result = await pipeline.anonymize(text)
        original = await pipeline.deanonymize(anonymized_text, mapping_id)
    """

    def __init__(self, workspace_id: str, ppi: PPIAnonymizer, redis: aioredis.Redis):
        self.workspace_id = workspace_id
        self.ppi = ppi
        self.redis = redis

    @classmethod
    async def for_workspace(cls, redis: aioredis.Redis, workspace_id: str) -> "PrivacyPipeline":
        """Load workspace-specific PPI terms from Redis and build the pipeline."""
        ppi_terms = list(DEFAULT_PPI_TERMS)

        raw = await redis.get(f"ws:{workspace_id}:ppi_terms")
        if raw:
            custom_terms: list[str] = json.loads(raw)
            # Merge: custom + defaults, deduplicate
            all_terms = list(dict.fromkeys(custom_terms + ppi_terms))
            ppi_terms = all_terms

        return cls(workspace_id, PPIAnonymizer(terms=ppi_terms), redis)

    # ── Anonymize ────────────────────────────────────────

    async def anonymize(self, text: str) -> tuple[str, str]:
        """Run the full 2-wave anonymization pipeline.

        Returns (anonymized_text, mapping_id).
        The mapping_id is an opaque key stored in Redis — callers never
        see the raw mapping, which prevents accidental leakage.
        """
        # Wave 1: PPI
        ppi_text, ppi_mapping = self.ppi.anonymize(text)
        if ppi_mapping:
            logger.info("PPI anonymized: %d terms replaced", len(ppi_mapping))

        # Wave 2: Presidio PII
        if settings.presidio_external_url:
            final_text, presidio_mapping = await presidio_engine.anonymize_via_external(
                settings.presidio_external_url, ppi_text
            )
        else:
            final_text, presidio_mapping = presidio_engine.anonymize(ppi_text)

        if presidio_mapping:
            logger.info("PII anonymized: %d entities replaced", len(presidio_mapping))

        # Merge mappings and store
        merged_mapping = {**presidio_mapping, **ppi_mapping}
        mapping_id = f"map:{self.workspace_id}:{uuid.uuid4().hex}"

        if merged_mapping:
            await self.redis.set(mapping_id, json.dumps(merged_mapping), ex=MAPPING_TTL)

        return final_text, mapping_id

    # ── Deanonymize ──────────────────────────────────────

    async def deanonymize(self, text: str, mapping_id: str) -> str:
        """Reverse the anonymization using the stored mapping."""
        raw = await self.redis.get(mapping_id)
        if not raw:
            logger.warning("Mapping not found: %s", mapping_id)
            return text

        mapping: dict[str, str] = json.loads(raw)

        # Separate PPI from Presidio mappings
        ppi_mapping = {k: v for k, v in mapping.items() if k.startswith("[PRODUCT_")}
        presidio_mapping = {k: v for k, v in mapping.items() if not k.startswith("[PRODUCT_")}

        result = text

        # Reverse Wave 2: Presidio
        if presidio_mapping:
            if settings.presidio_external_url:
                try:
                    result = await presidio_engine.deanonymize_via_external(
                        settings.presidio_external_url, result, presidio_mapping
                    )
                except Exception:
                    logger.warning("External Presidio deanonymize failed — local fallback")
                    result = presidio_engine.deanonymize(result, presidio_mapping)
            else:
                result = presidio_engine.deanonymize(result, presidio_mapping)

        # Reverse Wave 1: PPI
        result = PPIAnonymizer.deanonymize(result, ppi_mapping)

        return result
