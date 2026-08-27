from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from microscope_backend.core.config import settings
from fastapi.middleware.cors import CORSMiddleware
from starlette.exceptions import HTTPException as StarletteHTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.exception_handlers import http_exception_handler, request_validation_exception_handler
from microscope_backend.routers import user
from microscope_backend.core.database import engine

@asynccontextmanager
async def lifespan(_app: FastAPI):
    yield
    await engine.dispose()

app = FastAPI(
    title=settings.app_name,
    description="A search engine for the microscopic world | search everyday objects and see what they really look like under a microscope.",
    version="0.1.0",
    debug=settings.debug,
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_headers=["*"],
    allow_methods=["*"]
)

# App health route
@app.get("/health", tags=["Health"], status_code=200)
async def health_check():
    return {"status": "healthy"}

# App routers
app.include_router(user.router)

# Exception handlers
@app.exception_handler(StarletteHTTPException)
async def general_http_exception_handler(request: Request, exception: StarletteHTTPException):
    return await http_exception_handler(request, exception)

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exception: RequestValidationError):
    return await request_validation_exception_handler(request, exception)