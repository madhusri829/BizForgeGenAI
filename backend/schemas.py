from pydantic import BaseModel
from typing import List, Optional, Any
from datetime import datetime

# AI Service Schemas
class BrandRequest(BaseModel):
    description: str
    keywords: Optional[List[str]] = None

class TaglineRequest(BaseModel):
    brand_name: str
    description: str
    tone: Optional[str] = "catchy"

class ContentRequest(BaseModel):
    topic: str
    tone: str = "professional"
    content_type: str = "blog post"

class ProductDescriptionRequest(BaseModel):
    product_name: str
    features: str
    target_audience: str = "general"
    tone: str = "persuasive"

class SentimentRequest(BaseModel):
    text: str
    brand_name: Optional[str] = None

class TaglineAnalysisRequest(BaseModel):
    tagline: str
    brand_name: str
    brand_description: Optional[str] = None

class ColorsRequest(BaseModel):
    description: str

class ChatRequest(BaseModel):
    message: str
    history: Optional[List[dict]] = []

class LogoRequest(BaseModel):
    description: str
    style: Optional[str] = "modern, minimalist"

# Database Item Schemas
class SavedItemBase(BaseModel):
    item_type: str
    content: dict

class SavedItemCreate(SavedItemBase):
    pass

class SavedItem(SavedItemBase):
    id: int
    created_at: datetime
    class Config:
        from_attributes = True
