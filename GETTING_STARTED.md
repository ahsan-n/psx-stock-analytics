# Getting Started with PSX Stock Analytics Platform

This guide will help you set up and run the complete PSX Analytics platform with mock data.

## Prerequisites

Make sure you have the following installed:
- Docker Desktop (version 20.10+)
- Docker Compose (version 2.0+)
- Make (usually pre-installed on macOS/Linux)

## Quick Start

### 1. Create Environment File

First, create a `.env` file in the project root with the following content:

```bash
# Database
DATABASE_URL=postgresql://psx_user:psx_password@db:5432/psx_analytics
POSTGRES_USER=psx_user
POSTGRES_PASSWORD=psx_password
POSTGRES_DB=psx_analytics

# JWT
JWT_SECRET=your-super-secret-jwt-key-change-this-in-production
JWT_ALGORITHM=HS256
JWT_EXPIRATION_DAYS=7

# OpenAI (for Phase 3, not needed yet)
OPENAI_API_KEY=sk-your-openai-key-here

# Environment
ENVIRONMENT=development
DEBUG=true

# API
API_HOST=0.0.0.0
API_PORT=8000
```

Or simply run:
```bash
make setup
```

### 2. Start the Application

```bash
make dev
```

This command will:
- Build and start PostgreSQL database with pgvector
- Build and start the FastAPI backend
- Build and start the React frontend
- Set up all necessary Docker networks and volumes

**Initial startup takes 2-3 minutes** as it downloads images and installs dependencies.

### 3. Seed Mock Data

Once the containers are running, open a new terminal and run:

```bash
make seed
```

This will populate the database with FCCL (Fauji Cement Company Limited) mock financial data:
- 3 fiscal years (2022, 2023, 2024)
- Quarterly and annual statements
- Income Statement, Balance Sheet, Cash Flow
- Financial ratios (profitability, liquidity, leverage, efficiency)

### 4. Access the Application

Once seeding is complete, access:

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Alternative API Docs**: http://localhost:8000/redoc

### 5. Create Your First Account

1. Go to http://localhost:3000
2. Click "Sign up" on the login page
3. Create an account with any email (e.g., `test@example.com`)
4. You'll be automatically logged in

### 6. Explore the Dashboard

After login, you'll see:
1. **Home Page**: Overview of available companies
2. Click on **FCCL** to view detailed financial dashboard
3. Toggle between **Annual** and **Quarterly** views
4. Explore tabs:
   - **Income Statement**: Revenue, expenses, profit metrics
   - **Balance Sheet**: Assets, liabilities, equity
   - **Cash Flow**: Operating, investing, financing activities
   - **Ratios**: Profitability, liquidity, leverage, efficiency metrics

## Useful Commands

```bash
# View logs from all services
make logs

# Stop all services (keeps data)
make stop

# Start services again
make dev

# Clean up everything (removes containers and volumes)
make clean

# Access database shell
make shell-db

# Access backend shell
make shell-api

# Run migrations (if you modify models)
make migrate
```

## Troubleshooting

### Port Already in Use

If you get "port already in use" errors:

```bash
# Check what's using the port
lsof -i :3000  # Frontend
lsof -i :8000  # Backend
lsof -i :5432  # Database

# Kill the process or change ports in docker-compose.yml
```

### Database Connection Error

If backend can't connect to database:

```bash
# Check if database is ready
docker-compose ps

# Restart services
make stop
make dev
```

### Frontend Build Errors

If you see npm/node errors:

```bash
# Rebuild frontend container
docker-compose build frontend --no-cache
```

### Seed Data Already Exists

If you run `make seed` multiple times, you'll see:
```
⚠️  Data already exists. Skipping seed.
```

To re-seed:
```bash
make clean   # This removes all data
make dev     # Start fresh
make seed    # Seed again
```

## Project Structure

```
stockai/
├── backend/
│   ├── app/
│   │   ├── api/v1/          # API routes
│   │   ├── core/            # Config, database, security
│   │   ├── models/          # SQLAlchemy models
│   │   ├── schemas/         # Pydantic schemas
│   │   ├── main.py          # FastAPI app
│   │   └── seed.py          # Mock data seeding
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/      # Reusable components
│   │   ├── pages/           # Page components
│   │   ├── services/        # API service layer
│   │   ├── context/         # React context (auth)
│   │   └── App.tsx          # Main app component
│   ├── Dockerfile
│   └── package.json
├── docker-compose.yml       # Multi-container setup
├── Makefile                 # Developer commands
└── .env                     # Environment variables
```

## Next Steps

### Phase 2: PDF Processing
- Extract financial data from real FCCL annual reports
- Parse tables and statements from PDFs
- Replace mock data with real parsed data

### Phase 3: AI Integration
- Add OpenAI API key to `.env`
- Implement RAG (Retrieval Augmented Generation) pipeline
- Build chat interface for conversational insights
- Enable questions like "What was FCCL's revenue growth in 2023?"

## Development Tips

1. **Hot Reload**: Both frontend and backend have hot reload enabled
   - Changes to frontend code instantly refresh browser
   - Changes to backend code automatically restart server

2. **API Documentation**: FastAPI auto-generates interactive API docs
   - Visit http://localhost:8000/docs
   - Test endpoints directly in browser

3. **Database Inspection**: Use any PostgreSQL client
   - Host: localhost
   - Port: 5432
   - User: psx_user
   - Password: psx_password
   - Database: psx_analytics

4. **Logs**: Watch real-time logs with `make logs`

## Support

For issues or questions:
1. Check `docker-compose logs <service>` for errors
2. Ensure all ports (3000, 8000, 5432) are free
3. Verify Docker has enough resources (8GB RAM recommended)

Happy coding! 🚀
