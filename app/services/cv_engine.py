from __future__ import annotations

from typing import Any, Dict, List

from ..config import CV_TEMPLATE_MAP, CVVariant, PROFILE_DEFAULT_VARIANT, ProfileType
from ..models import CVInput, ExperienceItem
from .llm_client import generate_experience_bullets, generate_summary


def _build_experience_sections(
    cv_input: CVInput, target_role: str
) -> List[Dict[str, Any]]:
    if cv_input.profile_type != ProfileType.EXPERIENCED:
        return []

    sections: List[Dict[str, Any]] = []
    for exp in cv_input.experience:
        sections.append(
            _build_experience_section_item(exp, target_role),
        )
    return sections


def _build_experience_section_item(
    exp: ExperienceItem, target_role: str
) -> Dict[str, Any]:
    raw_bullets = generate_experience_bullets(exp, target_role)
    bullets = [line.strip() for line in raw_bullets.split("\n") if line.strip()]
    return {"item": exp, "bullets": bullets}


def _resolve_sections_order(profile_type: ProfileType) -> List[str]:
    if profile_type == ProfileType.EXPERIENCED:
        return ["summary", "experience", "skills", "education"]
    return ["summary", "education", "skills"]


def build_cv_context(cv_input: CVInput) -> Dict[str, Any]:
    """
    Buduje kontekst na potrzeby silnika szablonów (np. Jinja2).
    Obsługuje rozgałęzienie logiki dla profili doświadczonych i niedoświadczonych.
    """

    summary = generate_summary(cv_input)
    experience_sections = _build_experience_sections(cv_input, cv_input.target_role)

    context: Dict[str, Any] = {
        "full_name": cv_input.full_name,
        "email": cv_input.email,
        "phone": cv_input.phone,
        "target_role": cv_input.target_role,
        "summary": summary,
        "experience_sections": experience_sections,
        "education": cv_input.education,
        "skills": cv_input.skills,
        "sections_order": _resolve_sections_order(cv_input.profile_type),
        "profile_type": cv_input.profile_type.value,
        "cv_variant": cv_input.cv_variant.value,
    }

    return context


def choose_template(cv_input: CVInput) -> str:
    """
    Zwraca nazwę pliku szablonu HTML dla danego wariantu – z fallbackiem
    wynikającym z typu profilu użytkownika.
    """

    template = CV_TEMPLATE_MAP.get(cv_input.cv_variant)
    if template:
        return template

    fallback_variant = PROFILE_DEFAULT_VARIANT.get(cv_input.profile_type, CVVariant.VARIANT_A)
    return CV_TEMPLATE_MAP[fallback_variant]

