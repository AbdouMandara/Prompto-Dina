import logging

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import Limiter
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address
from starlette.middleware.base import BaseHTTPMiddleware

from core.config import settings
from services.prompt_service import build_prompt, suggest_improvements
from services.schemas import *

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(message)s',
)


def rate_limit_handler(request: Request, exc: Exception) -> JSONResponse:
    return JSONResponse(
        status_code=429,
        content={"detail": "Trop de requêtes. Veuillez réessayer dans une minute."},
    )


limiter = Limiter(key_func=get_remote_address, default_limits=["30/minute"])
app = FastAPI()
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, rate_limit_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
    allow_credentials=True,
)


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        return response


app.add_middleware(SecurityHeadersMiddleware)


@app.post('/generate_prompt', response_model=PromptResponse)
@limiter.limit("10/minute")
def generate_prompt(request: Request, data: PromptRequest):
    try:
        prompt = build_prompt(data)
        suggestions = suggest_improvements(data)
        return PromptResponse(prompt=prompt, suggestions=suggestions)
    except Exception:
        logging.exception("Erreur lors de la génération du prompt")
        return JSONResponse(
            status_code=500,
            content={"detail": "Erreur interne du serveur."},
        )


@app.get('/ping')
@limiter.limit("30/minute")
def ping(request: Request):
    return {'status': 'ok', 'message': 'Backend disponible'}


@app.get('/')
@limiter.limit("30/minute")
def read_root(request: Request):
    return {
        'message': 'Prompto~Dina est pret pour travailler'
    }
