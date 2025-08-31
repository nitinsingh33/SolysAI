# SolysAI - EV Sentiment Analysis Platform

🚀 **Advanced AI-powered sentiment analysis platform for Indian Electric Vehicle brands**

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Tech Stack](#tech-stack)
- [Installation](#installation)
- [Usage](#usage)
- [API Documentation](#api-documentation)
- [Deployment](#deployment)
- [Contributing](#contributing)

## 🎯 Overview

SolysAI is a comprehensive sentiment analysis platform that analyzes comments and reviews about Indian Electric Vehicle brands. It provides real-time insights, sentiment scoring, and temporal analysis using advanced AI models.

## ✨ Features

### 🤖 AI-Powered Analysis
- **Gemini AI Integration** - Advanced sentiment analysis
- **Real-time Processing** - Instant comment analysis
- **Multi-brand Support** - Tata, Mahindra, Ola, Ather, TVS, and more

### 📊 Analytics Dashboard
- **Interactive Charts** - Recharts-powered visualizations
- **Sentiment Distribution** - Positive, negative, neutral breakdown
- **Temporal Analysis** - Time-based sentiment trends
- **Brand Comparison** - Cross-brand sentiment comparison

### 🌐 Modern UI/UX
- **Premium Design** - Gradient backgrounds and animations
- **Responsive Layout** - Works on all devices
- **Real-time Updates** - Live data synchronization
- **Export Functionality** - Download analysis reports

## 🛠 Tech Stack

### Frontend
- **Framework**: Next.js 14 with TypeScript
- **Styling**: Tailwind CSS
- **Charts**: Recharts
- **Icons**: Lucide React
- **Animations**: Framer Motion

### Backend
- **Framework**: FastAPI (Python)
- **Database**: MongoDB with Motor (async)
- **AI**: Google Gemini AI
- **APIs**: YouTube Data API, Serper API
- **Server**: Uvicorn

### DevOps
- **Version Control**: Git
- **Environment**: Python Virtual Environment
- **Package Management**: npm, pip

## 🚀 Installation

### Prerequisites
- Node.js 18+ and npm
- Python 3.8+
- MongoDB (local or Atlas)
- Git

### 1. Clone Repository
```bash
git clone https://github.com/yourusername/solysai-ev-sentiment.git
cd solysai-ev-sentiment
```

### 2. Backend Setup
```bash
cd backend

# Create virtual environment
python -m venv .venv
.venv\Scripts\activate  # Windows
# source .venv/bin/activate  # macOS/Linux

# Install dependencies
pip install -r requirements.txt

# Setup environment variables
cp .env.example .env
# Edit .env with your API keys
```

### 3. Frontend Setup
```bash
cd frontend

# Install dependencies
npm install

# Setup environment variables
cp .env.local.example .env.local
# Edit .env.local with your configurations
```

### 4. Environment Variables

#### Backend (.env)
```env
# AI APIs
GEMINI_API_KEY=your_gemini_api_key_here
YOUTUBE_API_KEY=your_youtube_api_key_here
SERPER_API_KEY=your_serper_api_key_here

# Database
MONGODB_URL=mongodb://localhost:27017
DATABASE_NAME=ev_sentiment_db

# Application
ENVIRONMENT=development
DEBUG=true
```

#### Frontend (.env.local)
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_APP_NAME=SolysAI
```

## 🏃‍♂️ Usage

### Development Mode

#### Start Backend
```bash
cd backend
.venv\Scripts\activate
python main.py
```
Backend will run on: http://localhost:8000

#### Start Frontend
```bash
cd frontend
npm run dev
```
Frontend will run on: http://localhost:3000

### Production Build

#### Backend
```bash
cd backend
.venv\Scripts\activate
uvicorn main:app --host 0.0.0.0 --port 8000
```

#### Frontend
```bash
cd frontend
npm run build
npm start
```

## 📚 API Documentation

### Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET    | `/`      | Health check |
| GET    | `/health` | Service status |
| GET    | `/comments` | Get comments with filtering |
| GET    | `/comments/stats` | Get sentiment statistics |
| GET    | `/brands` | Get available brands |
| POST   | `/analyze` | Analyze text sentiment |

### API Documentation
- **Interactive Docs**: http://localhost:8000/docs
- **OpenAPI Schema**: http://localhost:8000/openapi.json

## 🌐 Deployment

### Vercel (Frontend)
1. Connect GitHub repository to Vercel
2. Set environment variables in Vercel dashboard
3. Deploy automatically on push

### Railway/Heroku (Backend)
1. Create new app
2. Connect GitHub repository
3. Set environment variables
4. Deploy

### Docker Deployment
```bash
# Build and run with Docker Compose
docker-compose up --build
```

## 📂 Project Structure

```
solysai-ev-sentiment/
├── backend/                 # FastAPI backend
│   ├── app/                # Application modules
│   │   ├── core/          # Core configurations
│   │   ├── models/        # Data models
│   │   └── services/      # Business logic
│   ├── main.py            # Application entry point
│   ├── requirements.txt   # Python dependencies
│   └── .env              # Environment variables
├── frontend/               # Next.js frontend
│   ├── pages/             # Page components
│   ├── styles/            # CSS styles
│   ├── package.json       # Node dependencies
│   └── .env.local         # Environment variables
├── .gitignore             # Git ignore rules
├── README.md              # Project documentation
└── docker-compose.yml     # Docker configuration
```

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/yourusername/solysai-ev-sentiment/issues)
- **Email**: support@solysai.com
- **Documentation**: [Wiki](https://github.com/yourusername/solysai-ev-sentiment/wiki)

## 🙏 Acknowledgments

- Google Gemini AI for sentiment analysis
- YouTube Data API for comment collection
- Recharts for beautiful visualizations
- Next.js and FastAPI communities

---

**Made with ❤️ for the EV community in India**
