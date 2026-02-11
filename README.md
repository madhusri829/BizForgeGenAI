# BizForge - AI-Powered Branding Suite

## Overview

BizForge is a comprehensive AI-powered branding platform that helps businesses create professional brand identities using cutting-edge artificial intelligence models. Whether you need logo generation, compelling copywriting, sentiment analysis, or color palettes, BizForge streamlines the entire branding process.

## Features

### 1. **AI Branding Chat** 
- Powered by IBM Granite 4.0
- Get instant branding advice and strategies
- Ask questions about logo design, messaging, positioning, and more
- Interactive conversation with AI expert

### 2. **Creative Text Generator**
- Powered by Groq LLAMA 3.3 70B
- Generate compelling brand taglines and marketing copy
- Create product descriptions, brand stories, and advertising content
- Customizable token length for different content types

### 3. **Logo Generator**
- Powered by Stable Diffusion XL
- Generate professional AI-designed logos
- Create multiple design options quickly
- Save generated images automatically

### 4. **Sentiment Analysis**
- Analyze tone and sentiment of your brand messaging
- Choose from Professional, Playful, Luxury tones
- Get insights into how your messaging will be perceived
- Perfect for refining your brand voice

### 5. **Color Palette Generator**
- Create harmonious color schemes for your brand
- Choose your brand tone and industry
- Get hex codes for easy implementation
- Professional color combinations based on psychology

### 6. **Voice Transcription**
- Convert audio files to text
- Perfect for brand interviews and voice notes
- Support for WAV audio files

## Tech Stack

### Backend
- **Framework**: FastAPI (Python)
- **AI Models**:
  - IBM Granite (Branding Chatbot)
  - Groq LLAMA 3.3 70B (Text Generation)
  - Stable Diffusion XL (Image Generation)
  - HuggingFace Models (Sentiment Analysis)
- **APIs**: 
  - Groq API for fast inference
  - HuggingFace Inference API
- **Additional**: 
  - Speech Recognition for voice transcription
  - PyTorch for model loading

### Frontend
- **HTML5**: Modern semantic markup
- **CSS3**: Advanced styling with CSS Grid and Flexbox
- **JavaScript**: Interactive features and API integration
- **Icons**: Font Awesome 6.0
- **Design**: Responsive mobile-first design

## Project Structure

```
BizForgeGenAI/
├── backend/
│   ├── main.py                 # FastAPI application with routes
│   ├── ai_services.py          # AI model implementations
│   ├── models.py               # Data models
│   ├── requirements.txt         # Python dependencies
│   └── __pycache__/
├── frontend/
│   ├── index.html              # Main dashboard
│   ├── branding.html           # Branding guide
│   ├── style.css               # Comprehensive styling
│   └── static/
│       ├── app.js              # Frontend JavaScript
│       └── generated_logos/    # Output folder for generated logos
└── README.md
```

## Installation

### Prerequisites
- Python 3.8+
- Node.js (optional, for serving frontend separately)
- Virtual environment (venv or conda)

### Backend Setup

1. **Create and activate virtual environment:**
```bash
cd backend
python -m venv venv
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

2. **Install dependencies:**
```bash
pip install -r requirements.txt
```

3. **Set up environment variables:**
Create a `.env` file in the backend directory:
```
GROQ_API_KEY=your_groq_api_key
HF_API_KEY=your_huggingface_api_key
```

3. **Run the backend:**
```bash
uvicorn main:app --reload
```

The backend will start at `http://localhost:8000`

### Frontend Setup

The frontend is served by the FastAPI backend, so no additional setup is needed. Simply open your browser and navigate to `http://localhost:8000`

## Usage

### Basic Workflow

1. **Open the Dashboard**
   - Navigate to `http://localhost:8000` in your browser
   - See all available AI tools

2. **Chat with AI**
   - Ask questions about your branding strategy
   - Get instant advice on logo, messaging, positioning

3. **Generate Content**
   - Create compelling taglines and copy
   - Generate professional logos
   - Generate color palettes

4. **Analyze & Refine**
   - Test your messaging with sentiment analysis
   - Validate your brand tone
   - Get feedback on how your message will be perceived

5. **Export & Use**
   - Download generated logos
   - Copy color codes
   - Use generated text in your materials

### API Endpoints

#### Chat with AI
```
POST /api/chat
Content-Type: application/json

{
  "message": "Your question about branding"
}

Response:
{
  "success": true,
  "response": "AI response text"
}
```

#### Generate Text
```
POST /api/generate-text
Content-Type: application/json

{
  "prompt": "Your prompt",
  "max_tokens": 150
}

Response:
{
  "success": true,
  "text": "Generated text"
}
```

#### Generate Logo
```
POST /api/generate-logo
Content-Type: application/json

{
  "prompt": "Description of your logo"
}

Response:
{
  "success": true,
  "image_url": "/static/generated_logos/logo_xxx.png"
}
```

#### Analyze Sentiment
```
POST /api/sentiment
Content-Type: application/json

{
  "text": "Brand message",
  "tone": "Professional"
}

Response:
{
  "success": true,
  "data": {
    "sentiment": "Positive",
    "tone": "Professional"
  }
}
```

#### Get Color Palette
```
POST /api/color-palette
Content-Type: application/json

{
  "tone": "Professional",
  "industry": "Tech"
}

Response:
{
  "success": true,
  "colors": ["#1A1A1A", "#0078D7", "#FFFFFF"]
}
```

## Configuration

### API Keys Required
1. **Groq API Key**: Get from https://console.groq.com
2. **HuggingFace API Key**: Get from https://huggingface.co/settings/tokens

### Model Selection
Edit `ai_services.py` to change:
- IBM Granite model variant
- LLAMA model version
- Stable Diffusion version
- Inference provider

## Styling & Customization

### Color Scheme
Edit CSS variables in `style.css`:
```css
:root {
  --primary-color: #0078d7;
  --secondary-color: #00a4ef;
  --accent-color: #ff6b6b;
  /* ... more variables */
}
```

### Font Family
Change `font-family` in body styles

### Layout
Modify `.container` max-width and padding

## Troubleshooting

### Backend Not Starting
- Check Python version (3.8+)
- Verify virtual environment is activated
- Check all dependencies are installed: `pip install -r requirements.txt`

### CSS Not Loading
- Check `style.css` is in the `/frontend/` directory
- Clear browser cache (Ctrl+Shift+Del)
- Check browser console for errors (F12)

### API Calls Failing
- Verify backend is running on `http://localhost:8000`
- Check CORS is enabled in FastAPI
- Verify API keys are set in environment variables

### Models Not Loading
- Ensure internet connection for downloading models
- Check HuggingFace API key is valid
- Verify sufficient disk space for models

## Performance Tips

1. **Use smaller models** for faster inference
2. **Cache results** for frequently requested content
3. **Batch API calls** when generating multiple assets
4. **Optimize images** before uploading
5. **Use CDN** for static assets in production

## Deployment

### Docker Deployment
```bash
docker build -t bizforge .
docker run -p 8000:8000 -e GROQ_API_KEY=xxx -e HF_API_KEY=xxx bizforge
```

### Cloud Deployment (AWS/GCP/Azure)
1. Deploy FastAPI backend to cloud function or container service
2. Deploy frontend to static hosting (S3, Netlify, etc.)
3. Update API base URL in `app.js` to cloud backend

### Environment Variables
```
GROQ_API_KEY=your_key
HF_API_KEY=your_key
LOG_LEVEL=info
MAX_WORKERS=4
```

## Security Considerations

1. **API Key Protection**: Never commit API keys to repositories
2. **CORS Security**: Restrict origins in production
3. **Rate Limiting**: Implement rate limiting for API endpoints
4. **Input Validation**: All user inputs are validated
5. **Error Handling**: Errors don't expose sensitive information

## Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## Future Features

- [ ] Brand guidebook PDF generation
- [ ] Brand equity analysis
- [ ] Competitor analysis
- [ ] Multi-language support
- [ ] Brand evolution tracking
- [ ] A/B testing dashboard
- [ ] Advanced analytics
- [ ] Template marketplace

## Limitations

- Max logo generation: 5 per minute
- Max text generation: 150 tokens default
- Image size: Up to 1024x1024
- File upload size: 25MB max
- Voice files: WAV format only

## License

MIT License - See LICENSE file for details

## Support

For issues, questions, or suggestions:
- Create an issue on GitHub
- Email: support@bizforge.com
- Documentation: https://docs.bizforge.com

## Credits

Built with:
- IBM Granite by IBM Research
- LLAMA by Meta
- Stable Diffusion by Stability AI
- FastAPI by Encode
- HuggingFace Community

## Changelog

### Version 1.0.0 (2026-02-11)
- Initial release
- Core AI features implemented
- Full-stack application
- Responsive design
- API documentation

---

**Last Updated**: February 11, 2026
**Version**: 1.0.0
#   B i z F o r g e G e n A I  
 