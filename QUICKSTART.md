# 🚀 PSX Analytics - Quick Start

## Start in 3 Commands

```bash
# 1. Setup environment (creates .env file)
make setup

# 2. Start all services (takes 2-3 minutes first time)
make dev

# 3. In a new terminal, seed mock data
make seed
```

## Access Your App

- **Frontend**: http://localhost:3000
- **API Docs**: http://localhost:8000/docs
- **Backend**: http://localhost:8000

## First Time Setup

1. Go to http://localhost:3000
2. Click **"Sign up"**
3. Create account (any email works, e.g., `test@example.com`)
4. Click on **FCCL** company card
5. Explore the financial dashboard!

## Dashboard Features

### 📊 Tabs
- **Income Statement**: Revenue, expenses, profitability
- **Balance Sheet**: Assets, liabilities, equity
- **Cash Flow**: Operating, investing, financing
- **Ratios**: 15+ financial ratios with trends

### 🔄 Period Toggle
- **Annual**: Yearly data (FY2022, FY2023, FY2024)
- **Quarterly**: Quarter-by-quarter (Q1-Q4)

### 📈 Visualizations
- Interactive data tables
- Trend line charts
- Ratio cards with YoY comparison

## Useful Commands

```bash
make logs      # View real-time logs
make stop      # Stop services
make clean     # Remove all data
make shell-api # Access backend terminal
```

## Mock Data Overview

The seed creates data for **FCCL (Fauji Cement Company Limited)**:
- 3 years: 2022, 2023, 2024
- Both annual and quarterly periods
- Income Statement, Balance Sheet, Cash Flow
- All financial ratios

## What's Next?

### Phase 2: Real PDF Data
Replace mock data with actual FCCL annual reports:
- Parse PDFs to extract tables
- Store real financial data
- Handle multiple report formats

### Phase 3: AI Chat Interface
Add conversational AI:
- Ask questions: "What was revenue growth in 2023?"
- Get answers with source citations
- Compare metrics across periods

## Troubleshooting

**Port already in use?**
```bash
lsof -i :3000   # Check what's using frontend port
lsof -i :8000   # Check backend
lsof -i :5432   # Check database
```

**Clean slate?**
```bash
make clean  # Removes everything
make dev    # Fresh start
make seed   # Re-seed data
```

**Not seeing data?**
- Wait 30 seconds after `make dev` before running `make seed`
- Check logs: `make logs`
- Database might still be initializing

## Project Files

```
stockai/
├── backend/           # FastAPI + SQLAlchemy
├── frontend/          # React + TypeScript
├── docker-compose.yml # Container orchestration
├── Makefile          # Developer commands
├── .env              # Configuration (don't commit!)
└── GETTING_STARTED.md # Detailed guide
```

## API Testing

Visit http://localhost:8000/docs to:
- View all API endpoints
- Test endpoints interactively
- See request/response schemas

## Support

- 📖 Read `GETTING_STARTED.md` for details
- 🏗️ Check `ARCHITECTURE.md` for technical overview
- 📝 See `project.md` for full project spec

---

**Happy analyzing! 📊**
