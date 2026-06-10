import logging
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from backend.routes import analyzer, tailor, network, interview, tracker
from backend.exceptions import CareerOSError

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(name)s  %(message)s",
)
logger = logging.getLogger("careeros")

app = FastAPI(
    title="CareerOS API",
    description="AI-powered career assistant — MVP using Gemini 2.5 Flash (free tier)",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tighten in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Global exception handler ──────────────────────────────────────────────────
@app.exception_handler(CareerOSError)
async def careeros_error_handler(request: Request, exc: CareerOSError) -> JSONResponse:
    """
    Catches every CareerOSError subclass and returns a structured JSON response.
    The frontend reads `detail.user_message` to display a clean error — no
    stack traces, no internal details ever reach the UI.
    """
    logger.error(
        "CareerOSError [%s] on %s %s — %s",
        exc.error_code,
        request.method,
        request.url.path,
        exc.user_message,
    )
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error_code": exc.error_code,
            "user_message": exc.user_message,
            # `detail` key mirrors FastAPI's HTTPException shape so the
            # frontend can use the same response-parsing logic
            "detail": exc.user_message,
        },
    )


@app.exception_handler(Exception)
async def unhandled_error_handler(request: Request, exc: Exception) -> JSONResponse:
    """
    Safety net for any exception that isn't a CareerOSError.
    Logs the full traceback server-side; sends a generic message to the client.
    """
    logger.exception(
        "Unhandled exception on %s %s", request.method, request.url.path
    )
    return JSONResponse(
        status_code=500,
        content={
            "error_code": "INTERNAL_ERROR",
            "user_message": (
                "An unexpected error occurred. "
                "Our team has been notified — please try again in a moment."
            ),
            "detail": (
                "An unexpected error occurred. Please try again."
            ),
        },
    )


# -- Routers ------------------------
app.include_router(analyzer.router)
app.include_router(tailor.router)
app.include_router(network.router)
app.include_router(interview.router)
app.include_router(tracker.router)


@app.get("/health")
def health():
    return {"status": "ok", "model": "gemini-2.5-flash"}

@app.get("/")
def root():
    return {"status": "ok"}
