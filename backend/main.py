from fastapi import FastAPI, Depends, Request, UploadFile, File
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from .config import settings
from .database import engine, get_db
from . import models, schemas
from .ai_service import ai_service

# Create tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title=settings.PROJECT_NAME, version=settings.PROJECT_VERSION)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.middleware("http")
async def log_requests(request: Request, call_next):
    print(f"Request: {request.method} {request.url}")
    response = await call_next(request)
    print(f"Response status: {response.status_code}")
    return response

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Templates
templates = Jinja2Templates(directory="templates")

@app.on_event("startup")
async def startup_event():
    print(f"Server accessible at: http://localhost:8000")
    print(f"HF_API_KEY loaded: {bool(settings.HF_API_KEY)}")
    if settings.HF_API_KEY:
        print(f"HF_API_KEY length: {len(settings.HF_API_KEY)}")

# --- Page Routes ---

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/index.html", response_class=HTMLResponse)
async def read_index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/brand-generator", response_class=HTMLResponse)
async def brand_generator_page(request: Request):
    return templates.TemplateResponse("brand_generator.html", {"request": request})

@app.get("/logo-studio", response_class=HTMLResponse)
async def logo_studio_page(request: Request):
    return templates.TemplateResponse("logo_studio.html", {"request": request})

@app.get("/content-ai", response_class=HTMLResponse)
async def content_ai_page(request: Request):
    return templates.TemplateResponse("content_ai.html", {"request": request})

@app.get("/sentiment", response_class=HTMLResponse)
async def sentiment_page(request: Request):
    return templates.TemplateResponse("sentiment.html", {"request": request})

@app.get("/chat-ui", response_class=HTMLResponse)
async def chat_page(request: Request):
    return templates.TemplateResponse("chat.html", {"request": request})

@app.get("/saved", response_class=HTMLResponse)
async def saved_page(request: Request):
    return templates.TemplateResponse("saved.html", {"request": request})

# --- API Routes ---

@app.post("/api/generate-brand")
async def generate_brand(req: schemas.BrandRequest):
    return await ai_service.generate_brand(req)

@app.post("/api/generate-tagline")
async def generate_tagline(req: schemas.TaglineRequest):
    return await ai_service.generate_tagline(req)

@app.post("/api/generate-content")
async def generate_content(req: schemas.ContentRequest):
    return await ai_service.generate_content(req)

@app.post("/api/generate-desc")
async def generate_product_desc(req: schemas.ProductDescriptionRequest):
    return await ai_service.generate_product_description(req)

@app.post("/api/analyze-sentiment")
async def analyze_sentiment(req: schemas.SentimentRequest):
    return await ai_service.analyze_sentiment(req)

@app.post("/api/analyze-tagline")
async def analyze_tagline(req: schemas.TaglineAnalysisRequest):
    return await ai_service.analyze_tagline(req)

@app.post("/api/get-colors")

@app.post("/api/get-colors")
async def get_colors(req: schemas.ColorsRequest):
    return await ai_service.get_colors(req)

@app.post("/api/chat")
async def chat(req: schemas.ChatRequest):
    return await ai_service.chat(req)

@app.post("/api/generate-logo")
async def generate_logo(req: schemas.LogoRequest):
    return await ai_service.generate_logo(req)

@app.post("/api/transcribe-voice")
async def transcribe_voice(file: UploadFile = File(...)):
    return await ai_service.transcribe_voice(file)

# Helper for saving items
@app.post("/api/save-item", response_model=schemas.SavedItem)
def save_item(item: schemas.SavedItemCreate, db: Session = Depends(get_db)):
    db_item = models.SavedItem(**item.dict())
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

@app.get("/api/saved-items", response_model=list[schemas.SavedItem])
def get_saved_items(db: Session = Depends(get_db)):
    return db.query(models.SavedItem).all()