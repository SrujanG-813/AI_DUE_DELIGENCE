# AI Due Diligence Engine

An AI-powered investment risk analysis system that automatically analyzes business documents and generates evidence-backed risk assessments.

![Tech Stack](https://img.shields.io/badge/Python-3.9+-blue)
![React](https://img.shields.io/badge/React-18-61dafb)
![FastAPI](https://img.shields.io/badge/FastAPI-0.109+-green)
![TypeScript](https://img.shields.io/badge/TypeScript-5.0+-blue)

## 🎯 What It Does

Upload business documents (contracts, financials, policies) and get:
- ✅ Automated risk analysis across Financial, Legal, and Operational dimensions
- ✅ Evidence-based findings with source citations
- ✅ Cross-document inconsistency detection
- ✅ Comprehensive risk reports with scores
- ✅ Beautiful web interface with interactive charts

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- Node.js 16+
- Mistral AI API key ([Get one FREE](https://console.mistral.ai/)) - Mistral offers generous free tier!

### Installation

1. **Clone the repository**
```bash
git clone <your-repo-url>
cd ai_due_diligence
```

2. **Install Python dependencies**
```bash
pip install -r requirements.txt
```

3. **Install Frontend dependencies**
```bash
cd frontend
npm install
cd ..
```

4. **Configure API Key**
```bash
# Copy .env.example to .env
cp .env.example .env

# Edit .env and add your FREE Mistral API key:
MISTRAL_API_KEY=your_key_here
```

### Run the Application

**One command starts everything:**

```bash
# Windows
start.bat

# PowerShell
.\start.ps1

# Cross-platform (npm)
npm start
```

This automatically:
- Starts backend API (Port 8000)
- Starts React frontend (Port 3000)
- Opens browser to http://localhost:3000

### Manual Start (Alternative)

```bash
# Terminal 1 - Backend
python api_server.py

# Terminal 2 - Frontend
cd frontend
npm run dev
```

## 🌐 Deploy to Railway

Deploy to Railway in one click:

[![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/template/your-template-id)

Or follow the [Railway Deployment Guide](RAILWAY_DEPLOYMENT.md) for manual setup.

**Required Environment Variables:**
- `MISTRAL_API_KEY` (FREE - get at console.mistral.ai)

## 📖 Documentation

- **[PROJECT_GUIDE.md](PROJECT_GUIDE.md)** - Complete technical guide for interviews
  - Architecture deep dive
  - Technology choices explained
  - Interview Q&A
  - Code walkthrough
  - Challenges & solutions

## 🏗️ Architecture

```
React Frontend (Port 3000)
         ↓
    FastAPI Backend (Port 8000)
         ↓
    Processing Pipeline:
    1. Document Ingestion (PDF/TXT)
    2. Text Chunking & Embedding
    3. Vector Storage (FAISS)
    4. AI Analysis (Mistral AI)
    5. Risk Scoring & Report
```

## 💻 Tech Stack

**Backend**
- FastAPI - Modern Python web framework
- LangChain - LLM orchestration
- Mistral AI - Large language model
- FAISS - Vector similarity search
- HuggingFace - Text embeddings

**Frontend**
- React 18 - UI framework
- TypeScript - Type safety
- Tailwind CSS - Styling
- Vite - Build tool
- Recharts - Data visualization

## ✨ Features

### Three AI Agents
- **Financial Risk Agent**: Revenue, growth, costs
- **Legal Risk Agent**: Contracts, liability, IP
- **Operational Risk Agent**: Personnel, vendors, scalability

### RAG Architecture
- Retrieval-Augmented Generation for accuracy
- Evidence-based analysis with citations
- No hallucinations - grounded in documents

### Beautiful UI
- Glass-morphism design
- Drag & drop file upload
- Real-time progress tracking
- Interactive risk charts
- Downloadable reports

## 🧪 Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=ai_due_diligence

# Run specific tests
pytest tests/test_agents.py
```

## 📁 Project Structure

```
ai_due_diligence/
├── ai_due_diligence/      # Core Python modules
│   ├── ingest.py          # Document processing
│   ├── agents.py          # Risk analysis agents
│   ├── cross_checks.py    # Inconsistency detection
│   └── report.py          # Report generation
├── frontend/              # React application
│   └── src/
│       ├── components/    # UI components
│       └── types/         # TypeScript types
├── tests/                 # Test suite
├── data/sample_docs/      # Sample documents
└── api_server.py          # FastAPI server
```

## 🎓 Learning Resources

See [PROJECT_GUIDE.md](PROJECT_GUIDE.md) for:
- Detailed architecture explanation
- Technology choice rationale
- Interview preparation
- Code deep dives
- Challenges & solutions

## 🔧 Configuration

### Environment Variables
```bash
MISTRAL_API_KEY=your_key_here  # Required
OPENAI_API_KEY=your_key_here   # Optional fallback
```

### API Endpoints
```
POST /api/analyze         # Upload and analyze documents
POST /api/analyze-sample  # Analyze sample documents
GET  /api/health          # System health check
```

## 🚧 Limitations

This is an MVP for educational purposes:
- Not production-ready (no auth, monitoring, scaling)
- Best for initial screening, not final decisions
- Requires internet for AI API calls
- English-optimized

## 📝 License

MIT License - See LICENSE file for details

## 🤝 Contributing

Contributions welcome! Please read the contribution guidelines first.

## 📧 Contact

For questions or feedback, please open an issue.

---

**Built with ❤️ using React, FastAPI, and Mistral AI**
