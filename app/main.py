import json

from fastapi import Body, FastAPI, Form, Request
from fastapi.responses import HTMLResponse, JSONResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from .config import CVVariant, ProfileType
from .models import CVInput, EducationItem, ExperienceItem
from .services.cv_engine import build_cv_context, choose_template
from .services.llm_client import chat_with_cv_coach, suggest_experience_raw
from .services.pdf_generator import html_to_pdf_bytes

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("main.html", {"request": request})


@app.post("/generate-cv", response_class=HTMLResponse)
async def generate_cv(
    request: Request,
    full_name: str = Form(...),
    email: str = Form(...),
    phone: str = Form(...),
    target_role: str = Form(...),
    profile_type: str = Form(...),
    cv_variant: str = Form(...),
    skills: str = Form(""),
    exp_role: str = Form(""),
    exp_company: str = Form(""),
    exp_start_year: int = Form(0),
    exp_end_year: int = Form(0),
    exp_description_raw: str = Form(""),
    edu_school: str = Form(""),
    edu_degree: str = Form(""),
    edu_start_year: int = Form(0),
    edu_end_year: int = Form(0),
):
    profile_enum = ProfileType(profile_type)
    variant_enum = CVVariant(cv_variant)

    skills_list = [s.strip() for s in skills.split(",") if s.strip()]

    experience_items = []
    if exp_role and exp_company and exp_start_year:
        experience_items.append(
            ExperienceItem(
                role=exp_role,
                company=exp_company,
                start_year=exp_start_year,
                end_year=exp_end_year or None,
                description_raw=exp_description_raw or None,
            )
        )

    education_items = []
    if edu_school and edu_degree:
        education_items.append(
            EducationItem(
                school=edu_school,
                degree=edu_degree,
                start_year=edu_start_year,
                end_year=edu_end_year,
            )
        )

    cv_input = CVInput(
        full_name=full_name,
        email=email,
        phone=phone,
        profile_type=profile_enum,
        cv_variant=variant_enum,
        target_role=target_role,
        education=education_items,
        experience=experience_items,
        skills=skills_list,
    )

    context = build_cv_context(cv_input)
    context["request"] = request

    template_name = choose_template(cv_input)
    return templates.TemplateResponse(template_name, context)


@app.post("/generate-pdf")
async def generate_pdf(request: Request, html: str = Form(...)):
    pdf_bytes = html_to_pdf_bytes(html)
    return StreamingResponse(
        iter([pdf_bytes]),
        media_type="application/pdf",
        headers={"Content-Disposition": 'attachment; filename="cv.pdf"'},
    )


@app.get("/assistant", response_class=HTMLResponse)
async def assistant_get(request: Request):
    messages = []
    history = json.dumps(messages, ensure_ascii=False)
    
    # Pobierz dane z query params (jeśli przekazane z formularza)
    candidate_data = {}
    if request.query_params:
        candidate_data = {
            "full_name": request.query_params.get("full_name", ""),
            "email": request.query_params.get("email", ""),
            "phone": request.query_params.get("phone", ""),
            "target_role": request.query_params.get("target_role", ""),
            "skills": request.query_params.get("skills", ""),
        }
    
    return templates.TemplateResponse(
        "assistant.html",
        {
            "request": request,
            "messages": messages,
            "history": history,
            "candidate_data": candidate_data,
        },
    )


@app.post("/assistant", response_class=HTMLResponse)
async def assistant_post(
    request: Request,
    user_input: str = Form(...),
    history: str = Form("[]"),
    full_name: str = Form(""),
    email: str = Form(""),
    phone: str = Form(""),
    target_role: str = Form(""),
    skills: str = Form(""),
):
    messages = json.loads(history)
    messages.append({"role": "user", "content": user_input})

    answer = chat_with_cv_coach(messages)
    messages.append({"role": "assistant", "content": answer})

    new_history = json.dumps(messages, ensure_ascii=False)
    
    # Przygotuj dane kandydata
    candidate_data = {}
    if full_name or email or phone or target_role or skills:
        candidate_data = {
            "full_name": full_name,
            "email": email,
            "phone": phone,
            "target_role": target_role,
            "skills": skills,
        }
    
    return templates.TemplateResponse(
        "assistant.html",
        {
            "request": request,
            "messages": messages,
            "history": new_history,
            "candidate_data": candidate_data,
        },
    )


@app.post("/api/suggest/experience")
async def api_suggest_experience(data: dict = Body(...)):
    role = data.get("role", "")
    company = data.get("company", "")
    target_role = data.get("target_role", "")

    if not role or not company or not target_role:
        return JSONResponse(
            {"error": "role, company i target_role są wymagane"},
            status_code=400,
        )

    variants = suggest_experience_raw(role, company, target_role)
    return {"variants": variants}


@app.post("/api/assistant/chat")
async def api_assistant_chat(data: dict = Body(...)):
    messages = data.get("messages", [])
    candidate_data = data.get("candidate_data", {})
    
    if not messages:
        return JSONResponse(
            {"error": "messages są wymagane"},
            status_code=400,
        )
    
    try:
        # Przekaż dane kandydata do funkcji chatu
        answer = chat_with_cv_coach(messages, candidate_data)
        return {"response": answer}
    except Exception as e:
        return JSONResponse(
            {"error": str(e)},
            status_code=500,
        )

