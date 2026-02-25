# Interview Cheat Sheet - AI Due Diligence Engine

## 🎯 30-Second Pitch
"AI-powered investment risk analysis system. Upload business documents, get automated risk assessment with evidence citations. Built with React + TypeScript frontend, FastAPI backend, and Mistral AI. Uses RAG architecture for accurate, grounded analysis."

## 📊 Quick Facts
- **Lines of Code**: 3,500+
- **Technologies**: 10+ (React, TypeScript, Python, FastAPI, Mistral AI, FAISS, etc.)
- **Components**: 8 React components, 5 Python modules
- **Analysis Time**: 2-5 minutes for 3-5 documents
- **Test Coverage**: Unit + Property-based tests

## 🏗️ Architecture (One Sentence Each)

1. **Frontend**: React 18 + TypeScript + Tailwind CSS for beautiful, type-safe UI
2. **Backend**: FastAPI REST API orchestrating the analysis pipeline
3. **Ingestion**: PyPDF2 extracts text, chunks into 1000-char pieces with 200 overlap
4. **Embeddings**: HuggingFace sentence-transformers (384-dim vectors, free)
5. **Vector Store**: FAISS for fast local similarity search
6. **Agents**: Three specialized agents (Financial, Legal, Operational) query vector store
7. **LLM**: Mistral AI analyzes retrieved chunks and generates findings
8. **Validation**: Heuristic cross-checks detect inconsistencies
9. **Scoring**: Weighted sum (High=3, Med=2, Low=1) with classification
10. **Report**: Markdown memo with all findings and citations

## 💻 Tech Stack (Why Each?)

| Technology | Why? |
|------------|------|
| **React** | Component-based, large ecosystem, industry standard |
| **TypeScript** | Type safety, catches errors early, better IDE support |
| **FastAPI** | Async, auto docs, type validation, modern Python |
| **Mistral AI** | Cost-effective, excellent performance, privacy-focused |
| **FAISS** | Fast, local, free, no external dependencies |
| **HuggingFace** | Free embeddings, no API key, good quality |
| **Tailwind** | Rapid styling, consistent design, responsive |
| **LangChain** | Abstracts LLM interactions, built-in RAG support |

## 🎤 Common Questions - Quick Answers

**Q: What is RAG?**
A: Retrieval-Augmented Generation. Instead of relying on LLM training data, we retrieve relevant document chunks and pass them as context. Prevents hallucinations, provides citations, works with new documents.

**Q: Why FAISS over cloud vector DB?**
A: Simplicity, local operation, free, fast for MVP scale. For production, I'd use Pinecone or Weaviate for scalability.

**Q: How do agents work?**
A: Each agent has domain-specific queries → retrieves relevant chunks → sends to Mistral AI → parses structured findings → returns with citations.

**Q: How would you scale this?**
A: 1) Containerize with Docker, 2) Deploy to cloud (AWS ECS), 3) Use cloud vector DB, 4) Add Redis caching, 5) Implement job queue (Celery), 6) Load balancer for multiple instances.

**Q: Biggest challenge?**
A: Environment variable loading - backend wasn't reading .env file. Fixed by adding load_dotenv() before imports. Taught me to always load env vars first.

**Q: What would you improve?**
A: 1) Authentication, 2) Batch processing, 3) More document types, 4) Custom risk categories, 5) Export options, 6) Production deployment.

## 🔧 Key Code Snippets to Know

### Backend - Agent Pattern
```python
class FinancialRiskAgent:
    def analyze(self):
        for query in self.queries:
            chunks = retrieve_relevant_chunks(self.vector_store, query)
            response = self.llm.invoke(f"Analyze: {chunks}")
            findings.extend(parse_findings(response))
        return findings
```

### Frontend - State Management
```typescript
const [analyzing, setAnalyzing] = useState(false)
const [results, setResults] = useState<AnalysisResults | null>(null)

const handleAnalyze = async () => {
  setAnalyzing(true)
  const response = await fetch('/api/analyze', {...})
  const data = await response.json()
  setResults(data)
  setAnalyzing(false)
}
```

### RAG - Retrieval
```python
# Embed query
query_vector = embeddings.embed_query(query)

# Search FAISS
distances, indices = vector_store.search(query_vector, k=5)

# Return chunks with metadata
return [chunks[i] for i in indices]
```

## 📁 File Structure (What's Where)

```
Backend:
- api_server.py       → FastAPI endpoints
- agents.py           → Three risk agents
- ingest.py           → Document processing
- cross_checks.py     → Inconsistency detection
- report.py           → Scoring & memo generation

Frontend:
- App.tsx             → Main app, state management
- FileUpload.tsx      → Drag & drop
- ResultsDashboard.tsx → Main results view
- RiskChart.tsx       → Recharts gauge
- FindingsCard.tsx    → Display findings

Config:
- .env                → API keys
- requirements.txt    → Python deps
- package.json        → Node deps
```

## 🎯 Demo Script (5 min)

1. **Open UI** (30s)
   - "Beautiful glass-morphism design with Tailwind"
   - "Drag & drop file upload"

2. **Start Analysis** (30s)
   - Click "Analyze Sample Documents"
   - "Uses three pre-loaded documents"

3. **Explain While Running** (2m)
   - "Backend extracts text, chunks it, generates embeddings"
   - "Three AI agents analyze: Financial, Legal, Operational"
   - "Each agent queries vector store, sends to Mistral AI"
   - "Cross-checks detect inconsistencies"
   - "Generates risk score and markdown memo"

4. **Show Results** (1m)
   - "Risk score gauge with classification"
   - "Findings by category with severity colors"
   - "Every finding has source citation"
   - "Full markdown memo at bottom"

5. **Show Code** (1m)
   - Open api_server.py: "FastAPI endpoint"
   - Open agents.py: "Agent implementation"
   - Open App.tsx: "React state management"

## 💡 Talking Points

### Technical Depth
- "Implemented RAG from scratch using FAISS and HuggingFace"
- "Built full REST API with async processing and error handling"
- "Type-safe frontend with TypeScript interfaces"
- "Comprehensive testing with pytest and Hypothesis"

### Problem Solving
- "Debugged environment variable loading issue"
- "Implemented dual provider support (Mistral/OpenAI)"
- "Created one-command startup for better UX"
- "Handled CORS, file uploads, temp file cleanup"

### Best Practices
- "Separation of concerns - each module has single responsibility"
- "Error handling with try-catch and cleanup in finally"
- "Type safety with TypeScript and Python type hints"
- "Comprehensive documentation for maintainability"

## 🚀 Confidence Boosters

✅ Full-stack (Frontend + Backend + AI)
✅ Modern tech stack (React 18, FastAPI, Mistral AI)
✅ Advanced AI (RAG, not just API calls)
✅ Production patterns (error handling, testing, docs)
✅ Beautiful UI (glass-morphism, responsive)
✅ User experience (one-command start)
✅ Well-documented (README, PROJECT_GUIDE)
✅ Tested (unit + property-based)

## 📝 Quick Metrics

- **Backend**: 1,500 lines Python
- **Frontend**: 1,200 lines TypeScript/TSX
- **Tests**: 800 lines
- **Modules**: 5 backend, 8 frontend components
- **API Endpoints**: 3
- **Test Files**: 4
- **Risk Categories**: 3
- **Cross-checks**: 3

## 🎓 What This Demonstrates

1. **Full-stack skills** - Can build complete applications
2. **AI/ML knowledge** - Understands RAG, embeddings, vector search
3. **Modern frameworks** - React, FastAPI, TypeScript
4. **API design** - RESTful, error handling, validation
5. **Testing** - Unit and property-based
6. **Documentation** - Clear, comprehensive
7. **Problem solving** - Debugged real issues
8. **UX focus** - Beautiful UI, easy setup

---

## 🔑 Key Takeaway

"This project shows I can build production-quality full-stack applications with modern AI integration, following best practices for code quality, testing, and documentation."

---

**Remember**: Be confident, explain your choices, show enthusiasm!
