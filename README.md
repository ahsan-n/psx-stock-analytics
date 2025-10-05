# PSX Stock Analytics Platform

AI-powered stock analytics platform for Pakistan Stock Exchange (PSX) that enables investors to interact with company annual reports through structured dashboards and conversational AI.

## Features

- 📊 **Financial Dashboards**: Interactive tables with Income Statement, Balance Sheet, Cash Flow, and Ratios
- 📈 **Data Visualization**: Charts and graphs for trend analysis
- 🔄 **Period Toggles**: Switch between quarterly and yearly views
- 🔐 **Authentication**: Secure JWT-based user authentication
- 🤖 **AI Chat** (Coming in Phase 3): Conversational insights from annual reports

## Quick Start

### Prerequisites

- Docker & Docker Compose
- Make (optional, for convenience commands)
- OpenAI API key (for Phase 3)

### Setup

```bash
# Clone and setup
make setup

# Start development environment
make dev
```

The application will be available at:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

### Development Commands

```bash
make dev        # Start all services
make stop       # Stop services
make clean      # Clean up containers and volumes
make migrate    # Run database migrations
make seed       # Seed mock data
make logs       # View logs
```

## Project Structure

```
stockai/
├── backend/           # FastAPI backend
│   ├── app/
│   │   ├── api/      # API routes
│   │   ├── models/   # Database models
│   │   ├── schemas/  # Pydantic schemas
│   │   └── core/     # Core utilities
│   └── alembic/      # Database migrations
├── frontend/         # React frontend
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   └── services/
│   └── public/
└── data/            # Persistent data
```

## Technology Stack

**Backend**
- FastAPI (Python 3.11+)
- PostgreSQL with pgvector
- SQLAlchemy + Alembic
- JWT authentication

**Frontend**
- React 18 + TypeScript
- Vite
- Tailwind CSS
- React Router
- Recharts

## Development Phases

- ✅ **Phase 1**: Foundation with mock data (Current)
- 🔄 **Phase 2**: PDF parsing and data extraction
- ⏳ **Phase 3**: AI/RAG integration for chat
- ⏳ **Phase 4**: Multi-company analysis and enhancements

## License

MIT
