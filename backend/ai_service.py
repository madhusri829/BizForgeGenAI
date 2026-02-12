"""
BizForge AI Services Module
Integration with Groq (LLaMA) and Hugging Face (IBM Granite) for AI generation
"""
import json
import os
import requests
import uuid
import base64
import traceback
from typing import Dict, Any, Optional, List
from io import BytesIO
from pathlib import Path

from groq import Groq
from huggingface_hub import InferenceClient
from PIL import Image
from fastapi import HTTPException, UploadFile

from .config import settings
from .schemas import BrandRequest, ContentRequest, SentimentRequest, ColorsRequest, ChatRequest, LogoRequest, TaglineRequest, ProductDescriptionRequest, TaglineAnalysisRequest

class AIService:
    """AI service for brand generation, content creation, and chat"""
    
    def __init__(self):
        self.groq_client = None
        self.hf_client = None
        
        if settings.GROQ_API_KEY:
            self.groq_client = Groq(api_key=settings.GROQ_API_KEY)
            
        # Initialize Google Gemini (Light Model)
        self.genai_model = None
        if settings.GOOGLE_API_KEY:
            try:
                import google.generativeai as genai
                genai.configure(api_key=settings.GOOGLE_API_KEY)
                # Try accessing gemini-pro which is generally available
                self.genai_model = genai.GenerativeModel('gemini-pro')
                print("✅ Google Gemini Pro activated")
            except ImportError:
                print("⚠️ google-generativeai not installed. Skipping.")
            except Exception as e:
                print(f"⚠️ Google Gemini init failed: {e}")
        
        if settings.HF_API_KEY:
            self.hf_client = InferenceClient(token=settings.HF_API_KEY)
        elif settings.HUGGINGFACE_TOKEN: # Support user's alternative env var name
            self.hf_client = InferenceClient(token=settings.HUGGINGFACE_TOKEN)
    
    async def _generate_text(self, prompt: str, system_instruction: str = None) -> str:
        """Helper to generate text using available LLM (Gemini preferred for 'light' usage, then Groq)"""
        
        # 1. Try Google Gemini (Light Model)
        if self.genai_model:
            try:
                # Gemini doesn't support system instructions directly in all versions, so we append
                full_prompt = f"{system_instruction}\n\n{prompt}" if system_instruction else prompt
                response = self.genai_model.generate_content(full_prompt)
                return response.text
            except Exception as e:
                print(f"⚠️ Gemini generation failed: {e}")
                # Fallback to Groq will happen below

        # 2. Fallback to Groq
        if self.groq_client:
            try:
                messages = []
                if system_instruction:
                    messages.append({"role": "system", "content": system_instruction})
                messages.append({"role": "user", "content": prompt})
                
                response = self.groq_client.chat.completions.create(
                    model=settings.GROQ_MODEL or "llama-3.3-70b-versatile",
                    messages=messages,
                    temperature=0.7
                )
                return response.choices[0].message.content
            except Exception as e_groq:
                print(f"⚠️ Groq generation failed: {e_groq}")
                raise e_groq
                
        raise Exception("No working LLM client available (Gemini or Groq)")

    def _extract_json(self, text: str) -> Any:
        try:
            # Try direct parse
            return json.loads(text)
        except json.JSONDecodeError:
            # Try to find JSON in code blocks or between braces
            import re
            json_match = re.search(r'\[.*\]|\{.*\}', text, re.DOTALL)
            if json_match:
                try:
                    return json.loads(json_match.group())
                except:
                    pass
            return None

    # --- API Compatible Methods ---

    async def generate_brand(self, req: BrandRequest):
        try:
            # Adapted from user's new implementation
            industry = "business" # generic fallback
            keywords = ", ".join(req.keywords) if req.keywords else ""
            
            prompt = f"""Generate 5 unique, memorable brand names for a business described as: '{req.description}'.
Keywords: {keywords}

Requirements:
- Creative and memorable
- Easy to pronounce
- Modern and professional

Return ONLY a valid JSON array of strings (e.g. ["Name1", "Name2"]). No other text."""
            

            
            result = await self._generate_text(prompt, "You are a creative brand naming expert. You always respond with ONLY valid JSON.")
            names = self._extract_json(result)
            
            # Fallback parsing if JSON fails but returns comma separated
            if not names and "," in result:
                 names = [n.strip() for n in result.split(",")]

            if isinstance(names, list):
                # Ensure they are strings
                clean_names = []
                for n in names:
                    if isinstance(n, dict) and 'name' in n:
                        clean_names.append(n['name'])
                    elif isinstance(n, str):
                        clean_names.append(n)
                return {"brand_names": clean_names}
            
            return {"brand_names": []}
        except Exception as e:
            print(f"Error generate_brand: {e}")
            raise HTTPException(status_code=500, detail=str(e))

    async def generate_tagline(self, req: TaglineRequest):
        try:
            prompt = f"""Generate 5 catchy and impactful taglines for the brand '{req.brand_name}', which is described as: '{req.description}'.
Tone: {req.tone}

Provide the output in valid JSON format as a list of objects, where each object has:
- "tagline": The tagline text
- "logic": A brief explanation of why this tagline works (marketing perspective)

Return ONLY valid JSON. No other text."""

            result = await self._generate_text(prompt, "You are a creative marketing copywriter. You always respond with ONLY valid JSON.")
            taglines = self._extract_json(result)
            
            if not taglines:
                # Basic fallback
                return {"taglines": [{"tagline": f"{req.brand_name}: The best choice.", "logic": "Generic fallback"}]}
                
            return {"taglines": taglines}
        except Exception as e:
            print(f"Error generate_tagline: {e}")
            raise HTTPException(status_code=500, detail=str(e))

    async def generate_logo(self, req: LogoRequest):
        try:
            print(f"Generating logo for: {req.description}")

            if not self.groq_client:
                raise Exception("Groq Client not initialized")

            # 1️⃣ Generate Prompt using LLM
            # Ask for specific visual elements rather than a story
            concept_prompt = f"""Generate a concise stable diffusion prompt for a logo for: '{req.description}'.
Style: {req.style}.
Requirements:
- Focus on the main subject/icon
- Use comma-separated keywords
- No clear text/letters
- Visual elements only

Example output: minimalist coffee cup, steam, brown and white, vector art, flat design, centered"""

            raw_prompt = await self._generate_text(concept_prompt)
            # Clean up the prompt
            raw_prompt = raw_prompt.replace('Prompt:', '').replace('"', '').strip()
            
            # Construct the final engineered prompt
            # We enforce the style constraints hard here
            image_prompt = f"logo of {req.description}, {raw_prompt}, vector, flattened, minimal, white background, high quality, 4k"
            print(f"Generated prompt: {image_prompt}")

            # 2️⃣ Generate Image using Lightweight Models
            image_url = None
            img_str = None

            if self.hf_client:

                # 🚀 Lightweight & Fast Models (Prioritized for speed and availability)
                # Adding more robust models for free tier
                models_to_try = [
                    {"id": "ByteDance/SDXL-Lightning", "steps": 8},  # Fast, specific step requirement
                    {"id": "runwayml/stable-diffusion-v1-5", "steps": 20}, # Reliable free one
                    {"id": "segmind/SSD-1B", "steps": 20},
                    {"id": "prompthero/openjourney", "steps": 20}
                ]
                
                image = None
                last_error = None

                for model_config in models_to_try:
                    model_id = model_config["id"]
                    steps = model_config["steps"]
                    try:
                        print(f"Trying model: {model_id}")
                        
                        image = self.hf_client.text_to_image(
                            image_prompt,
                            model=model_id,
                            guidance_scale=7.5,
                            num_inference_steps=steps, 
                            height=512,
                            width=512
                        )
                        print(f"✅ Success with {model_id}")
                        break
                    except Exception as e:
                        print(f"❌ {model_id} failed: {e}")
                        last_error = e

                # 4️⃣ 🛡️ Universal Fallback: Pollinations.ai (No Key Required) 🛡️
                if not image:
                    print("⚠️ All HF models failed. Engaging Pollinations.ai (Flux) fallback...")
                    try:
                        import requests
                        import urllib.parse
                        
                        # Use the engineered prompt which is now much cleaner
                        # Add 'vector' again to be safe
                        final_prompt = f"{image_prompt}, vector art, centered, no text"
                        if len(final_prompt) > 400:
                             # Just in case prompt is too long, trim
                             final_prompt = final_prompt[:400]

                        safe_prompt = urllib.parse.quote(final_prompt) 
                        
                        # Using 'flux' model for superior quality
                        url = f"https://image.pollinations.ai/prompt/{safe_prompt}?nologo=true&width=512&height=512&seed={uuid.uuid4().int % 10000}&model=flux"
                        
                        print(f"Fetching from: Pollinations.ai (Flux Mode)")
                        response = requests.get(url, timeout=60)
                        
                        if response.status_code == 200:
                            image = Image.open(BytesIO(response.content))
                            print("✅ Success with Pollinations.ai (Flux)")
                        else:
                            print(f"Pollinations returned status: {response.status_code}")
                            
                    except Exception as e_poll:
                        print(f"Pollinations failed: {e_poll}")

                if not image:
                    raise Exception(f"All models failed. Last error: {last_error}")

                # 3️⃣ Save Image
                logos_dir = Path("static/generated_logos")
                logos_dir.mkdir(parents=True, exist_ok=True)

                filename = f"logo_{uuid.uuid4().hex}.png"
                file_path = logos_dir / filename

                image.save(file_path, format="PNG")
                image_url = f"/static/generated_logos/{filename}"

                print(f"Saved to: {file_path}")

                # Convert to base64 (optional)
                buffered = BytesIO()
                image.save(buffered, format="PNG")
                img_str = base64.b64encode(buffered.getvalue()).decode()

            return {
                "prompt": image_prompt,
                "image": f"data:image/png;base64,{img_str}" if img_str else None,
                "file_url": image_url
            }

        except Exception as e:
            print(f"Error generating logo: {e}")
            print(traceback.format_exc())
            raise HTTPException(
                status_code=500,
                detail=f"Logo generation failed: {str(e)}"
            )
    async def generate_content(self, req: ContentRequest):
        try:
            prompt = f"Write a {req.content_type} about '{req.topic}' in a {req.tone} tone. Keep it engaging and concise."
            
            if not self.groq_client:
                 raise Exception("Groq Client not initialized")

            completion = self.groq_client.chat.completions.create(
                model=settings.GROQ_MODEL or "llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7
            )
            return {"content": completion.choices[0].message.content}
        except Exception as e:
            print(f"Error generate_content: {e}")
            raise HTTPException(status_code=500, detail=str(e))

    async def generate_product_description(self, req: ProductDescriptionRequest):
        try:
            prompt = f"""Create compelling product descriptions for '{req.product_name}'.
Features: {req.features}
Target Audience: {req.target_audience}
Tone: {req.tone}

Provide the output in valid JSON format with the following keys:
- "short_description": A 1-2 sentence summary suitable for a catalog card.
- "long_description": A detailed paragraph (3-4 sentences) describing the product benefits.
- "marketing_blurb": A catchy phrase or short paragraph for social media/ads.
- "bullets": A list of 5 customer-focused bullet points highlighting benefits.

Return ONLY valid JSON. No other text."""

            result = await self._generate_text(prompt, "You are an expert e-commerce copywriter. You always respond with ONLY valid JSON.")
            content = self._extract_json(result)
            
            if not content:
                # Fallback
                return {
                    "short_description": "Failed to generate description.",
                    "long_description": "Please try again.",
                    "marketing_blurb": "",
                    "bullets": []
                }
            return content

        except Exception as e:
            print(f"Error generate_product_description: {e}")
            raise HTTPException(status_code=500, detail=str(e))

    async def analyze_sentiment(self, req: SentimentRequest):
        try:
            brand_context = f" for the brand '{req.brand_name}'" if req.brand_name else ""
            prompt = f"""Analyze the following customer comments/reviews{brand_context}:

"{req.text}"

Provide a detailed analysis in valid JSON format with the following keys:
- "sentiment": "Positive", "Neutral", or "Negative"
- "score": A score from 0 to 100 (where 100 is perfect)
- "summary": A brief summary of the feedback (max 2 sentences)
- "key_issues": A list of specific problems or complaints mentioned
- "suggestions": A list of actionable recommendations for the brand to improve

Return ONLY valid JSON. Do not include markdown formatting or explanations."""

            result = await self._generate_text(prompt, "You are an expert brand analyst. You always respond with ONLY valid JSON.")
            analysis = self._extract_json(result)
            
            if not analysis:
                # Fallback if JSON parsing fails
                return {
                    "sentiment": "Neutral",
                    "score": 50,
                    "summary": "Could not parse detailed analysis.",
                    "key_issues": ["Analysis format error"],
                    "suggestions": ["Please try again with different text."]
                }
                
            return analysis
        except Exception as e:
            print(f"Error analyze_sentiment: {e}")
            raise HTTPException(status_code=500, detail=str(e))

    async def analyze_tagline(self, req: TaglineAnalysisRequest):
        try:
            brand_desc_ctx = f" described as '{req.brand_description}'" if req.brand_description else ""
            prompt = f"""Analyze this tagline for the brand '{req.brand_name}'{brand_desc_ctx}:
Tagline: "{req.tagline}"

Provide a detailed marketing assessment in valid JSON format with the following keys:
- "sentiment": "Positive", "Bold", "Playful", "Neutral", etc.
- "impact_score": A score from 0 to 100 for memorability and effectiveness.
- "reach_potential": "High", "Medium", or "Low" (likelihood to be shared or remembered).
- "analysis": A 2-3 sentence explanation of why the tagline works or doesn't work.
- "suggestions": A list of 3 concrete ways to improve it for better reach and impact.
- "better_alternatives": A list of 3 improved versions of the tagline.

Return ONLY valid JSON. No other text."""

            result = await self._generate_text(prompt, "You are a world-class brand strategist. You always respond with ONLY valid JSON.")
            analysis = self._extract_json(result)
            
            if not analysis:
                return {
                    "sentiment": "Unknown",
                    "impact_score": 0,
                    "reach_potential": "Low",
                    "analysis": "Could not analyze tagline.",
                    "suggestions": [],
                    "better_alternatives": []
                }
            return analysis
        except Exception as e:
            print(f"Error analyze_tagline: {e}")
            raise HTTPException(status_code=500, detail=str(e))

    async def get_colors(self, req: ColorsRequest):
        try:
            prompt = f"Suggest a color palette (5 colors) for a brand described as: '{req.description}'. Return ONLY the hex codes in a comma-separated list. do not include any other text."
            
            if not self.groq_client:
                 raise Exception("Groq Client not initialized")

            completion = self.groq_client.chat.completions.create(
                model=settings.GROQ_MODEL or "llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.5
            )
            colors_text = completion.choices[0].message.content
            colors = [c.strip() for c in colors_text.replace('\n', '').split(',') if c.strip().startswith('#')]
            return {"colors": colors}
        except Exception as e:
            print(f"Error get_colors: {e}")
            raise HTTPException(status_code=500, detail=str(e))

    async def chat(self, req: ChatRequest):
        try:
            if not self.groq_client:
                 raise Exception("Groq Client not initialized")

            messages = []
            for msg in req.history:
                role = "user" if msg.get("role") == "user" else "assistant"
                messages.append({"role": role, "content": msg.get("content")})
            messages.append({"role": "user", "content": req.message})

            response = self.groq_client.chat.completions.create(
                model=settings.GROQ_MODEL or "llama-3.3-70b-versatile",
                messages=messages,
                temperature=0.7,
                max_tokens=1000
            )
            return {"reply": response.choices[0].message.content}
        except Exception as e:
            print(f"Error chat: {e}")
            raise HTTPException(status_code=500, detail=str(e))

    async def transcribe_voice(self, file: UploadFile):
        try:
            if not self.groq_client:
                 raise Exception("Groq Client not initialized")

            content = await file.read()
            import tempfile
            with tempfile.NamedTemporaryFile(delete=False, suffix=".m4a") as tmp:
                tmp.write(content)
                tmp_path = tmp.name
            
            with open(tmp_path, "rb") as audio_file:
                transcription = self.groq_client.audio.transcriptions.create(
                    file=(file.filename, audio_file.read()),
                    model="distil-whisper-large-v3-en",
                    response_format="text"
                )
            os.unlink(tmp_path)
            return {"transcription": transcription}
        except Exception as e:
            print(f"Error transcribe_voice: {e}")
            raise HTTPException(status_code=500, detail=str(e))

ai_service = AIService()