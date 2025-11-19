from __future__ import annotations

from textwrap import dedent
from typing import Dict, List

from openai import OpenAI

from ..config import ModelConfig, ProfileType, get_model_config
from ..models import CVInput, ExperienceItem
from .rag_client import get_rag_context_for_cv

_model_config: ModelConfig = get_model_config()
_client = OpenAI(api_key=_model_config.api_key)


def _ensure_api_key_configured() -> None:
    if not _model_config.is_configured:
        raise RuntimeError(
            "OPENAI_API_KEY nie jest ustawione. Skonfiguruj je w env lub configu."
        )


def _compose_prompt(base_prompt: str, rag_chunks: List[str]) -> str:
    if not rag_chunks:
        return base_prompt
    rag_context = "\n\n".join(rag_chunks)
    return f"{base_prompt}\n\n{rag_context}"


def generate_summary(cv_input: CVInput) -> str:
    """
    Generuje podsumowanie zawodowe zależnie od profilu (doświadczony/niedoświadczony).
    """

    _ensure_api_key_configured()

    profile_label = (
        "osoba doświadczona"
        if cv_input.profile_type == ProfileType.EXPERIENCED
        else "osoba bez doświadczenia / junior"
    )

    base_prompt = dedent(
        f"""
        Jesteś asystentem piszącym CV.
        Napisz krótkie (3–4 zdania) podsumowanie zawodowe dla profilu: {profile_label}.
        Docelowa rola: {cv_input.target_role}.
        Imię i nazwisko: {cv_input.full_name}.
        Umiejętności: {", ".join(cv_input.skills) or "brak podanych umiejętności"}.
        Styl: konkretny, profesjonalny, bez lania wody.
        Nie używaj zwrotu 'jestem' na początku każdego zdania.
        """
    ).strip()

    prompt = _compose_prompt(base_prompt, get_rag_context_for_cv(base_prompt))

    response = _client.chat.completions.create(
        model=_model_config.model_name,
        messages=[
            {"role": "system", "content": "Jesteś ekspertem od pisania CV."},
            {"role": "user", "content": prompt},
        ],
    )
    return response.choices[0].message.content.strip()


def generate_experience_bullets(exp: ExperienceItem, target_role: str) -> str:
    """
    Generuje 3–5 punktów bullet dla pojedynczego doświadczenia.
    """

    _ensure_api_key_configured()

    base_prompt = dedent(
        f"""
        Na podstawie następującego doświadczenia wygeneruj 3–5 punktów bullet
        ukierunkowanych pod rolę: {target_role}.
        Stanowisko: {exp.role}
        Firma: {exp.company}
        Lata: {exp.start_year} - {exp.end_year or "obecnie"}
        Opis od użytkownika: {exp.description_raw or "brak"}
        Pisz po polsku, każdy punkt zaczynaj od czasownika, unikaj ogólników.
        """
    ).strip()

    prompt = _compose_prompt(
        base_prompt, get_rag_context_for_cv(f"{target_role}\n{base_prompt}")
    )

    response = _client.chat.completions.create(
        model=_model_config.model_name,
        messages=[
            {
                "role": "system",
                "content": "Jesteś ekspertem od pisania osiągnięć w CV.",
            },
            {"role": "user", "content": prompt},
        ],
    )
    return response.choices[0].message.content.strip()


def chat_with_cv_coach(
    messages: List[Dict[str, str]], candidate_data: Dict[str, str] = None
) -> str:
    """
    messages: lista {"role": "user"|"assistant", "content": "..."}
    candidate_data: słownik z danymi kandydata z formularza
    Zwraca odpowiedź asystenta.
    """
    _ensure_api_key_configured()

    # wyciągamy ostatnie pytanie usera do RAG
    last_user_msg = next(
        (m["content"] for m in reversed(messages) if m["role"] == "user"),
        "",
    )
    rag_ctx = get_rag_context_for_cv(last_user_msg, limit=5)
    rag_text = "\n\n".join(rag_ctx) if rag_ctx else ""

    # Przygotuj informacje o kandydacie
    candidate_info = ""
    if candidate_data:
        parts = []
        if candidate_data.get("full_name"):
            parts.append(f"Imię i nazwisko: {candidate_data['full_name']}")
        if candidate_data.get("target_role"):
            parts.append(f"Docelowa rola: {candidate_data['target_role']}")
        if candidate_data.get("skills"):
            parts.append(f"Umiejętności: {candidate_data['skills']}")
        if candidate_data.get("exp_role") and candidate_data.get("exp_company"):
            exp_info = f"Doświadczenie: {candidate_data['exp_role']} w {candidate_data['exp_company']}"
            if candidate_data.get("exp_description_raw"):
                exp_info += f"\nOpis: {candidate_data['exp_description_raw']}"
            parts.append(exp_info)
        if candidate_data.get("edu_degree") and candidate_data.get("edu_school"):
            parts.append(
                f"Edukacja: {candidate_data['edu_degree']} - {candidate_data['edu_school']}"
            )
        
        if parts:
            candidate_info = "\n\nInformacje o kandydacie:\n" + "\n".join(parts)

    system_prompt = dedent(
        f"""
        Jesteś asystentem CV (CV coach).
        Pomagasz użytkownikowi pisać CV, doradzasz co wpisać, jak strukturyzować doświadczenie
        i jak dopasować CV do oferty.

        {candidate_info}

        Możesz korzystać z poniższych wskazówek z bazy wiedzy:

        {rag_text}
        """
    ).strip()

    all_messages = [{"role": "system", "content": system_prompt}] + messages

    response = _client.chat.completions.create(
        model=_model_config.model_name,
        messages=all_messages,
    )
    return response.choices[0].message.content.strip()


def suggest_experience_raw(role: str, company: str, target_role: str) -> List[str]:
    """
    Zwraca kilka wariantów opisu doświadczenia (do wklejenia w exp_description_raw).
    """
    _ensure_api_key_configured()

    query = f"opis doświadczenia na stanowisku {role} w firmie {company} pod rolę {target_role}"
    rag_ctx = get_rag_context_for_cv(query, limit=5)
    rag_text = "\n\n".join(rag_ctx) if rag_ctx else ""

    prompt = dedent(
        f"""
        Na podstawie roli, firmy i roli docelowej zaproponuj 3 krótkie warianty opisu doświadczenia
        (2–3 zdania każdy), które użytkownik może wkleić do CV jako 'opis roli'.

        Stanowisko: {role}
        Firma: {company}
        Rola docelowa: {target_role}

        Baza wiedzy:
        {rag_text}

        Wypisz każdy wariant osobno, poprzedzony numerem (1., 2., 3.).
        """
    ).strip()

    response = _client.chat.completions.create(
        model=_model_config.model_name,
        messages=[
            {
                "role": "system",
                "content": "Jesteś ekspertem od opisu doświadczeń w CV.",
            },
            {"role": "user", "content": prompt},
        ],
    )
    text = response.choices[0].message.content.strip()
    lines = [l.strip() for l in text.split("\n") if l.strip()]
    variants = []
    for line in lines:
        # usuwamy "1.", "2." itp
        if line and line[0].isdigit():
            parts = line.split(".", 1)
            if len(parts) == 2:
                variants.append(parts[1].strip())
            else:
                variants.append(line)
        else:
            variants.append(line)
    return variants[:3]  # max 3 warianty

