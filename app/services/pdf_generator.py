from io import BytesIO

from xhtml2pdf import pisa


def html_to_pdf_bytes(html_content: str) -> bytes:
    """
    Konwertuje HTML na PDF i zwraca bytes (np. do odpowiedzi HTTP).
    """
    result = BytesIO()
    pisa.CreatePDF(src=html_content, dest=result)
    try:
        return result.getvalue()
    finally:
        result.close()

