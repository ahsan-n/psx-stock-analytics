# PSX Stock Analytics - Architecture Overview

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Frontend (Port 3000)                      │
│  React 18 + TypeScript + Vite + Tailwind CSS               │
│  ├── Authentication (Login/Register)                        │
│  ├── Company Overview (Home Page)                           │
│  └── Financial Dashboard                                    │
│      ├── Income Statement (Table + Chart)                   │
│      ├── Balance Sheet (Table + Chart)                      │
│      ├── Cash Flow (Table + Chart)                          │
│      └── Financial Ratios (Cards with trends)               │
└──────────────────┬──────────────────────────────────────────┘
                   │ HTTP/REST API
┌──────────────────┴──────────────────────────────────────────┐
│                    Backend (Port 8000)                       │
│  FastAPI + Python 3.11                                      │
│  ├── /api/v1/auth                                           │
│  │   ├── POST /register                                     │
│  │   ├── POST /login                                        │
│  │   └── GET  /me                                           │
│  ├── /api/v1/financial                                      │
│  │   ├── GET /companies                                     │
│  │   ├── GET /companies/{symbol}                            │
│  │   ├── GET /statements/{symbol}                           │
│  │   └── GET /ratios/{symbol}                               │
│  └── /api/v1/reports                                        │
│      └── GET /                                              │
└──────────────────┬──────────────────────────────────────────┘
                   │
┌──────────────────┴──────────────────────────────────────────┐
│                Database (Port 5432)                          │
│  PostgreSQL 16 + pgvector                                   │
│  ├── users (authentication)                                 │
│  ├── companies (PSX companies)                              │
│  ├── financial_statements                                   │
│  ├── financial_metrics                                      │
│  └── financial_ratios                                       │
└──────────────────────────────────────────────────────────────┘
```

## Technology Stack

### Backend
- **Framework**: FastAPI 0.109
- **ORM**: SQLAlchemy 2.0
- **Database**: PostgreSQL 16 with pgvector extension
- **Authentication**: JWT with bcrypt password hashing
- **API Documentation**: Auto-generated OpenAPI/Swagger

### Frontend
- **Framework**: React 18 with TypeScript
- **Build Tool**: Vite 5 (fast HMR and building)
- **Styling**: Tailwind CSS 3.4
- **Routing**: React Router 6
- **Charts**: Recharts 2.10
- **Icons**: Lucide React
- **HTTP Client**: Axios

### Infrastructure
- **Containerization**: Docker + Docker Compose
- **Development**: Hot reload for both frontend and backend
- **Automation**: Makefile for common tasks

## Database Schema

### Core Tables

**users**
```sql
- id: INTEGER PRIMARY KEY
- email: VARCHAR UNIQUE
- hashed_password: VARCHAR
- full_name: VARCHAR (optional)
- created_at: TIMESTAMP
- updated_at: TIMESTAMP
```

**companies**
```sql
- id: INTEGER PRIMARY KEY
- symbol: VARCHAR UNIQUE (e.g., "FCCL")
- name: VARCHAR (e.g., "Fauji Cement Company Limited")
- sector: VARCHAR (e.g., "Cement")
- created_at: TIMESTAMP
```

**financial_statements**
```sql
- id: INTEGER PRIMARY KEY
- company_id: INTEGER FK -> companies
- statement_type: ENUM (income_statement, balance_sheet, cash_flow)
- period_type: ENUM (quarterly, annual)
- fiscal_year: INTEGER
- quarter: INTEGER (nullable, 1-4)
- period_end_date: DATE
- created_at: TIMESTAMP
```

**financial_metrics**
```sql
- id: INTEGER PRIMARY KEY
- statement_id: INTEGER FK -> financial_statements
- company_id: INTEGER FK -> companies
- metric_name: VARCHAR (e.g., "revenue", "net_income")
- metric_label: VARCHAR (e.g., "Revenue", "Net Income")
- value: FLOAT
- unit: VARCHAR (default "PKR")
- created_at: TIMESTAMP
```

**financial_ratios**
```sql
- id: INTEGER PRIMARY KEY
- company_id: INTEGER FK -> companies
- fiscal_year: INTEGER
- quarter: INTEGER (nullable)
- period_type: ENUM (quarterly, annual)
- gross_profit_margin: FLOAT
- operating_profit_margin: FLOAT
- net_profit_margin: FLOAT
- return_on_assets: FLOAT
- return_on_equity: FLOAT
- current_ratio: FLOAT
- quick_ratio: FLOAT
- cash_ratio: FLOAT
- debt_to_equity: FLOAT
- debt_to_assets: FLOAT
- equity_multiplier: FLOAT
- asset_turnover: FLOAT
- inventory_turnover: FLOAT
- receivables_turnover: FLOAT
- created_at: TIMESTAMP
```

## API Endpoints

### Authentication
- `POST /api/v1/auth/register` - Create new user account
- `POST /api/v1/auth/login` - Login and receive JWT token
- `GET /api/v1/auth/me` - Get current user info (requires auth)

### Financial Data
- `GET /api/v1/financial/companies` - List all companies
- `GET /api/v1/financial/companies/{symbol}` - Get company details
- `GET /api/v1/financial/statements/{symbol}` - Get financial statements
  - Query params: `statement_type`, `period_type`, `fiscal_year`
- `GET /api/v1/financial/ratios/{symbol}` - Get financial ratios
  - Query params: `period_type`, `fiscal_year`

### Reports
- `GET /api/v1/reports/` - List available company reports

## Frontend Components

### Pages
- **LoginPage** - User authentication
- **RegisterPage** - New user registration
- **HomePage** - Company overview and selection
- **CompanyPage** - Financial dashboard with tabs

### Components
- **Layout** - Header with navigation and logout
- **PrivateRoute** - Protected route wrapper
- **FinancialTable** - Data table for financial statements
- **FinancialChart** - Line charts for trend analysis
- **RatiosCard** - Financial ratios with trend indicators

### Services
- **api.ts** - Axios-based API client with interceptors

### Context
- **AuthContext** - Global authentication state management

## Data Flow

### Authentication Flow
1. User submits credentials via login form
2. Frontend sends POST to `/api/v1/auth/login`
3. Backend verifies credentials, returns JWT
4. Frontend stores JWT in localStorage
5. Subsequent requests include JWT in Authorization header
6. Backend validates JWT on protected endpoints

### Financial Data Flow
1. User navigates to company page (e.g., `/FCCL`)
2. Frontend requests company info and financial data
3. Backend queries PostgreSQL for statements and ratios
4. Data is returned as JSON
5. Frontend renders tables and charts
6. User toggles period type (quarterly/annual)
7. Frontend re-fetches data with updated parameters

## Mock Data Structure

The seed script generates:
- **1 Company**: FCCL (Fauji Cement Company Limited)
- **3 Fiscal Years**: 2022, 2023, 2024
- **5 Periods per Year**: 1 annual + 4 quarterly
- **3 Statement Types**: Income Statement, Balance Sheet, Cash Flow
- **Financial Ratios**: 15 key ratios per period

Total: 45 financial statements with ~500 metrics

## Security

### Authentication
- Passwords hashed with bcrypt (cost factor 12)
- JWT tokens with 7-day expiry
- HS256 algorithm for token signing
- Tokens validated on every protected endpoint

### Data Access
- All financial endpoints require authentication
- Users can access all company data (public information)
- Chat history will be user-specific (Phase 3)

### API Security
- CORS enabled for localhost:3000
- Request/response validation with Pydantic
- SQL injection prevented via ORM
- Input sanitization on all endpoints

## Performance

### Response Times (Target)
- Authentication: < 200ms
- Company list: < 300ms
- Financial statements: < 500ms
- Chart data: < 600ms

### Optimization Strategies
- Database indexes on foreign keys and frequently queried fields
- Connection pooling (max 20 connections)
- Frontend component memoization
- Lazy loading for charts

## Future Enhancements (Phase 2-4)

### Phase 2: PDF Processing
- Extract text from real annual reports
- Parse financial tables using PyMuPDF or LlamaParse
- Replace mock data with parsed data
- Handle multiple report formats

### Phase 3: AI/RAG Integration
- Embed financial documents with OpenAI
- Vector search with pgvector
- Chat interface with streaming responses
- Source citations linking to PDF pages

### Phase 4: Advanced Features
- Multi-company comparisons
- Sector-level analytics
- AI-generated stock analysis reports
- Export functionality
- Admin dashboard

## Development Workflow

1. **Start Development**
   ```bash
   make dev
   ```

2. **Make Changes**
   - Backend: Edit files in `backend/app/`, server auto-reloads
   - Frontend: Edit files in `frontend/src/`, browser auto-refreshes

3. **Add Database Changes**
   ```bash
   # Modify models in backend/app/models/
   make migrate  # Generate and run migrations
   ```

4. **Test Changes**
   ```bash
   make test
   ```

5. **View Logs**
   ```bash
   make logs
   ```

## Deployment Considerations

### Environment Variables
- Set strong JWT_SECRET in production
- Use managed PostgreSQL (e.g., AWS RDS, Supabase)
- Add OpenAI API key for AI features

### Scaling
- Backend: Increase Uvicorn workers
- Database: Read replicas for queries
- Frontend: CDN for static assets
- Add Redis for caching embeddings (Phase 3)

### Monitoring
- Add Sentry for error tracking
- Implement structured logging
- Monitor API response times
- Track OpenAI API usage and costs

## Testing Strategy

### Backend Tests
- Unit tests for business logic
- Integration tests for API endpoints
- Database transaction rollbacks in tests

### Frontend Tests
- Component tests with React Testing Library
- E2E tests with Playwright (optional)

### Manual Testing
- API testing via `/docs` (Swagger UI)
- Browser testing across Chrome, Safari, Firefox
