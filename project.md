# PSX Stock Analytics Platform - MVP Project Specification

## Project Vision

Build an AI-powered stock analytics platform for Pakistan Stock Exchange (PSX) that enables investors to interact conversationally with company annual reports. The MVP focuses on proving the core value proposition: **transforming dense financial PDFs into accessible AI-driven insights**.

### Core Hypothesis
Pakistani retail investors struggle with financial literacy (26% nationally) and analyzing 200+ page annual reports. An AI chatbot that answers questions like "What was FCCL's revenue growth?" or "Compare profit margins across sectors" dramatically lowers the barrier to fundamental analysis.

### Success Criteria
- Users can upload/view PSX company annual reports
- AI accurately answers financial questions with source citations
- Response time < 3 seconds for 90% of queries
- System handles 3 reports initially, architecture scales to 500+ PSX companies

---

## Development Philosophy

### Phased AI Introduction
We deliberately **delay full AI integration** until foundations are solid. This prevents:
- Building complex chat UIs before validating RAG works
- Accumulating OpenAI costs during basic development
- Coupling AI logic with core application architecture

### Phase Strategy
1. **Foundation First**: Auth, database, PDF viewing (no AI costs)
2. **AI Proof-of-Concept**: Validate RAG pipeline with one report
3. **Full Integration**: Production chat interface with all features
4. **Enhancement**: Multi-stock analysis, advanced prompts

---

## Technical Architecture

### System Overview
```
┌─────────────────────────────────────────────────────────────┐
│                         Frontend Layer                       │
│  React + TypeScript + Tailwind + Vite                       │
│  - Auth UI (Login/Register)                                 │
│  - Dashboard (Sidebar: Reports | Main: Chat/Viewer)         │
│  - Streaming Chat Interface                                 │
└────────────────┬────────────────────────────────────────────┘
                 │ HTTP/WebSocket
┌────────────────┴────────────────────────────────────────────┐
│                      API Layer (FastAPI)                     │
│  - JWT Authentication Endpoints                             │
│  - Report Management (upload, list, retrieve)               │
│  - Chat Endpoints (streaming, history)                      │
│  - RAG Pipeline Orchestration                               │
└────────────────┬────────────────────────────────────────────┘
                 │
        ┌────────┴─────────┐
        │                  │
┌───────▼──────┐  ┌────────▼─────────────────────────────────┐
│  PostgreSQL  │  │     AI/RAG Layer (LangChain)             │
│              │  │  - PDF Processing (PyMuPDF/LlamaParse)   │
│  - Users     │  │  - Text Chunking (RecursiveCharacter)    │
│  - Reports   │  │  - OpenAI Embeddings (text-embedding-3)  │
│  - Messages  │  │  - Vector Search (pgvector)              │
│  - pgvector  │  │  - LLM Generation (GPT-4o-mini)          │
└──────────────┘  └──────────────────────────────────────────┘
```

### Technology Stack

**Backend**
- FastAPI: API framework with automatic OpenAPI docs
- PostgreSQL + pgvector: Unified relational + vector storage
- SQLAlchemy: ORM with Alembic migrations
- LangChain: RAG orchestration framework
- PyMuPDF or LlamaParse: PDF text extraction
- Python 3.11+

**Frontend**
- React 18+ with TypeScript
- Vite: Build tool (faster than CRA)
- Tailwind CSS: Utility-first styling
- Axios: API client
- React Router: Navigation
- Streaming support for chat responses

**Infrastructure**
- Docker Compose: Multi-container orchestration
- Makefile: Developer workflow automation
- OpenAPI Schema: Auto-generated from FastAPI
- JWT: Stateless authentication

**Optional Enhancements** (Post-MVP)
- Redis: Cache embeddings and frequent queries
- Nginx: Reverse proxy for production
- Sentry: Error tracking
- Pre-commit: Code quality hooks

---

## Data Architecture

### Database Schema (Core Tables)

**users**
- id, email, hashed_password, created_at
- Purpose: JWT-based authentication

**reports**
- id, company_symbol, company_name, fiscal_year, file_path, upload_date, processed
- Purpose: Track uploaded annual reports metadata

**report_chunks**
- id, report_id, content, page_number, chunk_index, embedding (vector)
- Purpose: Store processed text chunks with pgvector embeddings

**chat_sessions**
- id, user_id, report_id, created_at
- Purpose: Group related messages

**messages**
- id, session_id, role (user/assistant), content, sources (JSON), timestamp
- Purpose: Chat history with source citations

### Vector Storage Strategy
- Use pgvector extension in PostgreSQL (simpler than separate vector DB)
- Embedding dimension: 1536 (OpenAI text-embedding-3-small)
- Index: HNSW for fast approximate nearest neighbor search
- Store embeddings directly in report_chunks table

---

## Phase 1: Foundation (No AI)

### Objective
Build authentication, database, and report viewing capabilities. Validate PDF parsing works correctly.

### Requirements

**Authentication**
- User registration with email + password
- Login returns JWT token (7-day expiry)
- Protected routes verify JWT on each request
- Password hashing with bcrypt

**Report Management**
- API endpoint to upload PDF files
- Store PDFs in `/data/reports/{company_symbol}/{year}/` directory
- Database record with metadata (company, year, file path)
- List all reports endpoint (paginated)
- Retrieve single report endpoint (stream PDF)

**UI Components**
- Login/Register pages
- Dashboard layout: sidebar (reports list) + main area (content)
- PDF viewer component (use browser native or pdf.js)
- Basic navigation and routing

**Data Setup**
- Manually download 3 FCCL annual reports (FY2022, FY2023, FY2024)
- Upload via API or seed script
- Verify PDFs display correctly in viewer

### Deliverables
- Users can register, login, view reports
- No AI functionality yet
- Clean separation of concerns for Phase 2 integration

---

## Phase 2: AI Proof-of-Concept

### Objective
Validate the RAG pipeline works with ONE report before building full chat interface. This is a technical checkpoint.

### Requirements

**PDF Processing Pipeline**
- Extract text from single FCCL report (choose latest year)
- Chunk text into ~1000 token segments with 200 token overlap
- Preserve page numbers and section context
- Handle tables and financial statements intelligently

**Embedding Generation**
- Use OpenAI text-embedding-3-small model
- Generate embeddings for all chunks
- Store in report_chunks table with pgvector
- Create HNSW index for fast retrieval

**Test RAG Endpoint**
- Single API endpoint: `POST /api/chat/test`
- Input: User question (string)
- Process:
  1. Embed question
  2. Vector search top 5 relevant chunks
  3. Pass chunks + question to GPT-4o-mini
  4. Return answer with source page numbers
- Output: JSON with answer and sources

**Validation Criteria**
- Ask 5 test questions about FCCL report
- Verify answers are factually correct
- Verify source citations match actual pages
- Response time < 3 seconds

### Deliverables
- Working RAG pipeline for one report
- Proof that PDF parsing captures financial data correctly
- Confidence to build full chat UI in Phase 3

---

## Phase 3: Full AI Integration

### Objective
Build production-ready chat interface with streaming responses, chat history, and support for all 3 reports.

### Requirements

**Process Remaining Reports**
- Embed remaining 2 FCCL reports using Phase 2 pipeline
- All 3 reports queryable via chat
- Specify report context in chat (e.g., "In FY2023 report, what was...")

**Chat Interface**
- Chat window with message history (user/assistant)
- Input box with send button
- Streaming responses (word-by-word typing effect)
- Display source citations below answers (page numbers, clickable to PDF)
- Clear chat / New conversation functionality

**Chat API Endpoints**
- `POST /api/chat/sessions` - Create new chat session
- `GET /api/chat/sessions` - List user's chat sessions
- `POST /api/chat/sessions/{id}/messages` - Send message (streaming response)
- `GET /api/chat/sessions/{id}/messages` - Retrieve chat history

**RAG Enhancements**
- Context-aware prompts: "You are a financial analyst for PSX companies..."
- Include company name, fiscal year in context
- Format answers with bullet points for readability
- Handle follow-up questions (maintain conversation context)

**Chat History**
- Save all user/assistant messages to database
- Associate messages with chat sessions
- Users can resume previous conversations
- Sidebar shows recent chat sessions

### Deliverables
- Fully functional chat experience
- Users can analyze all 3 FCCL reports via conversation
- Answers include verifiable sources
- Chat history persists across sessions

---

## Phase 4: Enhancement (Post-MVP)

### Future Capabilities
- Multi-company comparison: "Compare FCCL and ENGRO revenue growth"
- Generate AI stock analysis reports (like SimplyWallStreet)
- Sector-level insights across multiple companies
- Upload custom reports (extend beyond FCCL)
- Better table/chart extraction from PDFs
- Export chat conversations as PDF
- Admin panel to manage reports

### Optimization
- Cache frequent embeddings in Redis
- Improve chunking strategy based on user feedback
- Fine-tune prompts for Pakistani financial terminology
- Add analytics on common questions

---

## API Design Principles

### OpenAPI Schema
FastAPI auto-generates OpenAPI docs at `/docs` and `/redoc`. All endpoints must:
- Include request/response schemas with Pydantic models
- Document authentication requirements
- Provide example requests/responses
- Use semantic HTTP status codes

### REST Conventions
- `GET /api/reports` - List reports
- `POST /api/reports` - Upload report
- `GET /api/reports/{id}` - Retrieve report
- `POST /api/auth/register` - Create user
- `POST /api/auth/login` - Get JWT token
- `POST /api/chat/sessions` - Create chat session
- `POST /api/chat/sessions/{id}/messages` - Send message (streaming)

### Response Format
```json
{
  "success": true,
  "data": { ... },
  "error": null
}
```

### Error Handling
- 400: Bad request (validation errors)
- 401: Unauthorized (invalid/missing JWT)
- 404: Resource not found
- 500: Server error
- Return structured error messages with actionable feedback

---

## Development Workflow

### Makefile Commands
```makefile
make setup          # Initial setup (env, dependencies)
make dev            # Start development environment
make migrate        # Run database migrations
make seed           # Seed initial data (FCCL reports)
make test           # Run test suite
make lint           # Code quality checks
make clean          # Clean up containers/volumes
```

### Docker Compose Services
- `api`: FastAPI backend on port 8000
- `db`: PostgreSQL with pgvector on port 5432
- `frontend`: React dev server on port 3000
- Volumes for persistent data and hot-reloading

### Environment Variables
```bash
# .env file
DATABASE_URL=postgresql://user:pass@db:5432/psx_analytics
JWT_SECRET=your-secret-key-here
OPENAI_API_KEY=sk-...
ENVIRONMENT=development
```

---

## Security Considerations

### Authentication
- Passwords hashed with bcrypt (cost factor 12)
- JWT tokens signed with HS256
- Tokens include user_id and expiry (7 days)
- Frontend stores JWT in localStorage (acceptable for MVP)
- All chat/report endpoints require valid JWT

### Data Privacy
- Users can only access their own chat history
- Reports are shared across users (public annual reports)
- No PII stored beyond email/password
- SQL injection prevented via SQLAlchemy ORM parameterization

### Rate Limiting (Future)
- Limit chat messages to 20/minute per user
- Prevents OpenAI cost abuse
- Implement in Phase 4

---

## Performance Targets

### Response Times
- Authentication: < 200ms
- Report list: < 300ms
- PDF retrieval: < 500ms (streaming large files)
- Chat response (non-streaming): < 3 seconds
- Chat response (streaming): First token < 1 second

### Scalability (MVP)
- Support 10 concurrent users
- Handle 100 reports in database
- 1000 chat messages per day
- OpenAI cost: ~$0.02 per query (embedding + generation)

### Database
- pgvector HNSW index for < 100ms vector search
- Proper indexes on foreign keys and frequently queried fields
- Connection pooling (max 20 connections)

---

## Success Metrics

### Technical Metrics
- RAG accuracy: 90%+ correct answers to test questions
- Source citation accuracy: 95%+ correct page references
- System uptime: 99%+ during development
- API response time: 95th percentile < 3s

### User Experience Metrics
- User can complete "ask 3 questions about FCCL" flow in < 2 minutes
- Chat interface feels responsive (streaming effect)
- PDF viewing works across browsers
- No confusion about which report is being queried

### Business Validation
- MVP proves RAG works for Pakistani financial reports
- Architecture confirmed to scale to 500+ PSX companies
- Foundation ready for Phase 4 enhancements
- Cost model validated: ~$0.02/query sustainable

---

## Critical Dependencies

### External Services
- OpenAI API: Embeddings + LLM (requires API key with credit)
- PostgreSQL with pgvector: Vector extension must be installed

### Data Requirements
- 3 FCCL annual reports (PDF format, manually downloaded from PSX)
- Reports should be text-based PDFs (not scanned images)
- Typical size: 50-200 pages, 5-20 MB each

### Development Environment
- Docker + Docker Compose
- Minimum 8GB RAM (for local LLM experiments if needed)
- Node.js 18+ for frontend
- Python 3.11+ for backend

---

## Risk Mitigation

### PDF Quality Issues
- **Risk**: Scanned PDFs or poor quality tables
- **Mitigation**: Test parsing in Phase 1, consider LlamaParse for complex layouts

### OpenAI Costs
- **Risk**: Excessive API usage during development
- **Mitigation**: Phase 2 validates pipeline before full integration, use GPT-4o-mini (cheap)

### RAG Accuracy
- **Risk**: AI gives incorrect financial information
- **Mitigation**: Always show source citations, Phase 2 validation checkpoint

### Authentication Complexity
- **Risk**: JWT implementation delays core development
- **Mitigation**: Use proven libraries (python-jose, passlib), keep simple

### Scope Creep
- **Risk**: Adding features before MVP complete
- **Mitigation**: Strict phase gates, Phase 4 for enhancements

---

## Getting Started Checklist

### Prerequisites
- [ ] OpenAI API key with credit
- [ ] Docker and Docker Compose installed
- [ ] Download 3 FCCL annual reports from PSX website
- [ ] Basic familiarity with FastAPI and React

### Phase 1 Kickoff
- [ ] Run `make setup` to initialize project
- [ ] Verify database connection and migrations
- [ ] Create first user via registration endpoint
- [ ] Upload one FCCL report and view in browser
- [ ] Confirm JWT authentication works

### Phase 2 Kickoff
- [ ] Extract text from one report, inspect quality
- [ ] Generate embeddings, verify stored in pgvector
- [ ] Test RAG endpoint with 5 questions
- [ ] Achieve 90%+ accuracy before proceeding

### Phase 3 Kickoff
- [ ] Build chat UI with streaming
- [ ] Process remaining 2 reports
- [ ] Implement chat history
- [ ] End-to-end testing with real users

---

## Notes for AI Assistants (Claude/Cursor)

When implementing this project:

1. **Start with Phase 1 completely** before any AI code
2. **Use FastAPI dependency injection** for database sessions and JWT verification
3. **Frontend component structure**: Keep auth, chat, and reports as separate route-level components
4. **RAG chunking**: Use LangChain's RecursiveCharacterTextSplitter with smart separators for financial documents
5. **Streaming**: Use FastAPI's StreamingResponse with Server-Sent Events for chat
6. **Error boundaries**: Wrap chat interface in error boundary to prevent UI crashes
7. **Testing strategy**: Unit tests for RAG pipeline, integration tests for API endpoints
8. **Migrations**: Use Alembic from the start, never alter tables manually
9. **API versioning**: All endpoints under `/api/v1/` for future compatibility
10. **Documentation**: Docstrings on all public functions, README with setup instructions

**Most Important**: Each phase should be fully functional and demoable before moving to the next. Don't write Phase 3 code in Phase 1.