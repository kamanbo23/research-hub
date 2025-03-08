# Research Application Deployment Guide

This guide provides instructions for deploying the Research Application without Docker.

## Prerequisites

- Python 3.9+
- Node.js 18+
- PostgreSQL database (or a Supabase account)
- Vercel account (for frontend hosting)
- Render account (for backend hosting) or Railway/Heroku

## Deployment Options

### Option 1: Using Render Blueprint (Recommended)

1. Fork this repository to your GitHub account
2. Sign up for a [Render](https://render.com/) account
3. Connect your GitHub account to Render
4. Click "New +" > "Blueprint" and select your forked repository
5. Render will deploy both the backend API and a PostgreSQL database

### Option 2: Manual Deployment

#### Backend Deployment

1. Sign up for [Render](https://render.com/) or [Railway](https://railway.app/)
2. Create a new Web Service, connect to your GitHub repo
3. Set the following configuration:
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `gunicorn -w 4 -k uvicorn.workers.UvicornWorker main:app --bind 0.0.0.0:$PORT`
   - Environment Variables:
     - `DATABASE_URL`: Your PostgreSQL connection string
     - `SECRET_KEY`: A secure random string
     - `ALGORITHM`: HS256
     - `ACCESS_TOKEN_EXPIRE_MINUTES`: 30

#### Database Options

**Option A: Supabase (Free Tier)**
1. Sign up for [Supabase](https://supabase.com/)
2. Create a new project
3. Go to Project Settings > Database to get your connection string
4. Add the connection string as the `DATABASE_URL` environment variable in your backend deployment

**Option B: ElephantSQL (Free Tier)**
1. Sign up for [ElephantSQL](https://www.elephantsql.com/)
2. Create a new instance (Tiny Turtle plan is free)
3. Get the connection URL and add it as the `DATABASE_URL` environment variable

#### Frontend Deployment

1. Sign up for [Vercel](https://vercel.com/)
2. Connect your GitHub repository
3. Set the build configuration:
   - Framework Preset: Create React App
   - Build Command: `npm run build`
   - Output Directory: `build`
4. Add the following environment variable:
   - `REACT_APP_API_URL`: Your deployed backend URL (e.g., https://researchapp-api.onrender.com)

5. Deploy!

## Local Development

### Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload
```

### Frontend
```bash
cd frontend
npm install
npm start
```

## Database Initialization

After deploying the database, you need to initialize it and create an admin user:

1. Connect to your deployed backend URL
2. Run the admin creation endpoint: `/admin/create` with the appropriate JSON payload
3. Or use the provided scripts: 