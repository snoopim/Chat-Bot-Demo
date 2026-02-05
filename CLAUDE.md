# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

A GDPR RoPA (Record of Processing Activities) chatbot application that guides users through documenting data processing activities for compliance. Users answer questions about their data processes, and the system validates answers using AI, then exports completed flows to Excel (RoPA format) or Word documents.

## Tech Stack

- **Backend**: Django 6.0 + Django REST Framework
- **Frontend**: Next.js 16 with React 19, TypeScript, Tailwind CSS 4
- **Database**: SQLite (default) with dj-database-url for configuration
- **AI**: OpenAI API for answer validation and typo checking

## Development Commands

### Backend (Django)
```bash
# Activate virtual environment
source .venv/bin/activate

# Run development server (default port 8000, frontend expects 8001)
python manage.py runserver 8001

# Database migrations
python manage.py makemigrations
python manage.py migrate
```

### Frontend (Next.js)
```bash
cd frontend-next
npm run dev      # Development server on port 3000
npm run build    # Production build
npm run lint     # ESLint
```

## Architecture

### Backend Structure (`flows/` app)

- **models.py**: `ProcessFlow` (tracks a RoPA process) and `ProcessFlowAnswer` (individual question answers)
- **questions.py**: `PROCESS_FLOW_QUESTIONS` list defining all RoPA questions with dependencies via `depends_on`
- **views.py**: REST API views including answer validation, progress tracking, and export (Excel/DOCX)
- **ai.py**: OpenAI integration for `judge_flow_answer()` (validates answer clarity) and `typo_check_text()`

### Frontend Structure (`frontend-next/app/`)

- **page.tsx**: Main single-page application with sidebar (process list/creation) and main panel (question flow)
- **lib/api.ts**: Axios client pointing to `http://127.0.0.1:8001/api`
- **lib/types.ts**: TypeScript types for ProcessFlow, Progress, AiResult
- **lib/processes.ts**: Predefined process name groups
- **components/**: `BotBubble` (AI feedback display), `Tag` (status badges)

### Key Flows

1. **Question Dependencies**: Questions can have `depends_on: {key, value}` - child questions auto-hide or show "Not applicable" based on parent answers
2. **Progress Tracking**: Backend computes next recommended question; flow marked "completed" only when ALL questions answered
3. **AI Validation**: Before saving, answers go through OpenAI to check clarity for RoPA documentation
4. **Typo Check**: Popup offers spelling/grammar fixes before final submission

## Environment Variables

Backend `.env` (in `backend/`):
- `OPENAI_API_KEY` - Required for AI validation features
- `OPENAI_MODEL` - Model name (default: gpt-5.2)
- `DATABASE_URL` - Optional, defaults to SQLite

Frontend uses `NEXT_PUBLIC_API_BASE` to override the API URL (defaults to `http://127.0.0.1:8001/api`).

## CORS Configuration

Backend allows origins: `localhost:3000`, `localhost:3001`, `127.0.0.1:3000`, `127.0.0.1:3001`
