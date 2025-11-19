import os
from dataclasses import dataclass
from enum import Enum
from typing import Dict


class ProfileType(str, Enum):
    EXPERIENCED = "experienced"
    INEXPERIENCED = "inexperienced"


class CVVariant(str, Enum):
    VARIANT_A = "variant_a"
    VARIANT_B = "variant_b"


DEFAULT_MODEL_NAME = os.getenv("OPENAI_MODEL_NAME", "gpt-4.1-mini")
FALLBACK_API_KEY = "WSTAW_TUTAJ_ALBO_UZYJ_ENV"
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", FALLBACK_API_KEY)


@dataclass(frozen=True)
class ModelConfig:
    api_key: str = OPENAI_API_KEY
    model_name: str = DEFAULT_MODEL_NAME

    @property
    def is_configured(self) -> bool:
        return self.api_key not in {"", FALLBACK_API_KEY}


CV_TEMPLATE_MAP: Dict[CVVariant, str] = {
    CVVariant.VARIANT_A: "cv_variant_a.html",
    CVVariant.VARIANT_B: "cv_variant_b.html",
}


PROFILE_DEFAULT_VARIANT: Dict[ProfileType, CVVariant] = {
    ProfileType.EXPERIENCED: CVVariant.VARIANT_A,
    ProfileType.INEXPERIENCED: CVVariant.VARIANT_B,
}


def get_model_config() -> ModelConfig:
    """
    Zwraca aktualną konfigurację modelu OpenAI.
    """
    return ModelConfig()

