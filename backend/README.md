# EV Sentiment Analysis Platform - Backend

## 🚀 Overview

This is the FastAPI backend for the EV Sentiment Analysis Platform, providing AI-powered sentiment analysis for Indian Electric Vehicle brands.

## 🏗️ Architecture

```
backend/
├── app/
│   ├── api/           # API endpoints and routes
│   ├── core/          # Configuration and database
│   ├── models/        # Pydantic data models
│   ├── services/      # Business logic services
│   └── utils/         # Utility functions
├── requirements.txt   # Python dependencies
└── test_backend.py   # Testing script
```

## 🛠️ Technology Stack

- **Framework**: FastAPI 0.104.1
- **Database**: MongoDB (with Motor async driver)
- **Cache**: Redis
- **AI**: OpenAI GPT-3.5 / Google Gemini
- **Data Source**: YouTube Comments API
- **Language**: Python 3.9+

## ⚡ Quick Start

### 1. Environment Setup

Create `.env` file in the backend directory:

```env
# Database
MONGODB_URL=mongodb://localhost:27017
REDIS_URL=redis://localhost:6379

# AI APIs
OPENAI_API_KEY=your_openai_api_key_here
GEMINI_API_KEY=your_gemini_api_key_here

# Application
ENVIRONMENT=development
PROJECT_NAME=EV-Sentiment-Analysis
SECRET_KEY=your_secret_key_here
```

### 2. Install Dependencies

```bash
# Install Python dependencies
pip install -r requirements.txt
```

### 3. Test Backend

```bash
# Run backend tests
python test_backend.py
```

### 4. Start Development Server

```bash
# Start FastAPI server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## 📚 API Documentation

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health

## 🚗 Supported EV Brands

1. **Ola Electric** - S1, S1 Pro, S1 Air
2. **Ather Energy** - 450X, 450 Plus
3. **TVS Motor** - iQube Electric
4. **Bajaj Auto** - Chetak Electric
5. **Hero Electric** - Vida V1
6. **Revolt Motors** - RV400, RV300
7. **Tata Motors** - Nexon EV, Tigor EV
8. **Mahindra** - e2oPlus, eVerito
9. **MG Motor** - ZS EV, Comet EV
10. **Hyundai** - Kona Electric, Ioniq 5

## 🧠 AI Features

### Sentiment Analysis
- **Labels**: Positive, Negative, Neutral, Mixed
- **Emotions**: Joy, Anger, Fear, Sadness, Surprise, Disgust, Trust, Anticipation
- **Aspects**: Battery, Performance, Design, Build Quality, Features, Service, Price, Charging

### Advanced Features
- **Sarcasm Detection**: Identifies sarcastic comments
- **Brand Comparison**: Detects comparative statements
- **Spam Filtering**: Removes low-quality comments
- **Bot Detection**: Filters automated comments

## 📊 Data Models

### Comment Model
```python
{
    "text": "Comment content",
    "author": "Username",
    "video_id": "YouTube video ID",
    "brand_mentioned": "Brand identifier",
    "source": "youtube",
    "scraped_at": "2025-01-01T00:00:00Z"
}
```

### Sentiment Analysis Model
```python
{
    "sentiment_label": "positive",
    "sentiment_score": 0.8,
    "confidence_score": 0.95,
    "emotions": {"joy": 0.7, "trust": 0.6},
    "aspects": {"battery": 0.9, "performance": 0.8}
}
```

## 🔧 Services

### YouTube Scraper
- **Rate Limited**: 3600 requests/hour
- **Brand Detection**: Automatic brand identification
- **Content Filtering**: Spam and bot detection
- **Async Processing**: Non-blocking operations

### Sentiment Analyzer
- **Multiple Providers**: OpenAI, Gemini, Rule-based fallback
- **Batch Processing**: Efficient bulk analysis
- **Caching**: Redis-based result caching
- **Error Handling**: Graceful fallback mechanisms

## 📈 Performance

- **Async Architecture**: Non-blocking I/O operations
- **Database Indexing**: Optimized MongoDB queries
- **Redis Caching**: Fast data retrieval
- **Batch Processing**: Efficient bulk operations

## 🧪 Testing

```bash
# Run all backend tests
python test_backend.py

# Expected output:
✅ Database connection successful
✅ Comment model validation successful
✅ Sentiment analysis successful
✅ YouTube scraper initialization successful
✅ Configuration test successful
```

## 🔐 Security

- **Input Validation**: Pydantic model validation
- **Rate Limiting**: API request throttling
- **CORS**: Configurable cross-origin requests
- **Environment Variables**: Secure configuration

## 📝 Development

### Adding New Endpoints
1. Create route in `app/api/`
2. Add data models in `app/models/`
3. Implement business logic in `app/services/`
4. Include router in `app/main.py`

### Testing New Features
1. Add tests to `test_backend.py`
2. Run testing script
3. Check API documentation
4. Verify database operations

## 🚀 Deployment

### Docker (Recommended)
```bash
# Build Docker image
docker build -t ev-sentiment-backend .

# Run container
docker run -p 8000:8000 ev-sentiment-backend
```

### Production Environment
```bash
# Install production dependencies
pip install -r requirements.txt

# Run with Gunicorn
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker
```

## 📊 Monitoring

- **Health Endpoint**: `/health` for uptime monitoring
- **Logging**: Structured logging with timestamps
- **Metrics**: Request counting and timing
- **Error Tracking**: Exception logging and handling

## 🤝 Contributing

1. Follow PEP 8 style guidelines
2. Add type hints to all functions
3. Write comprehensive docstrings
4. Include unit tests for new features
5. Update documentation for API changes

## 📞 Support

For technical support or questions:
- Check API documentation at `/docs`
- Run backend tests with `python test_backend.py`
- Review logs for error messages
- Ensure all environment variables are set

---

**Built with ❤️ for the Indian EV ecosystem**
