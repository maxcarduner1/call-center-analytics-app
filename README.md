# Call Center Transcript Analytics App

A professional web application for viewing and analyzing call center transcripts with automated quality scorecards. Built with FastAPI and Databricks Lakebase integration, this app displays AI-generated quality assessments of customer service calls.

## Technologies Used

- **FastAPI**: High-performance web framework for building APIs
- **Uvicorn**: ASGI server for running the FastAPI application
- **Python-dotenv**: Environment variable management
- **Databricks SDK**: Integration with Databricks services and Lakebase
- **PostgreSQL**: Database backend via psycopg2 (Lakebase autoscaling PostgreSQL)
- **HTML5/CSS3**: Modern, responsive frontend design

## Features

### 🎯 Core Functionality

- **Call List View**: Browse all call center transcripts with key metrics
- **Quality Scores**: View AI-generated quality scores for each call (0-60 scale)
- **Detailed Scorecards**: Drill down into specific scoring criteria:
  - Technical Aspects (Recording Disclosure, Member Authentication, Call Closing)
  - Quality of Service (Professionalism, Program Information, Demeanor)
- **Full Transcripts**: Read complete call transcripts
- **Advanced Filtering**: Filter calls by member ID, date range, and minimum score

### 🎨 User Experience

- **Professional Dashboard**: Clean, call center-focused interface
- **Color-Coded Scores**: Visual indicators (green/yellow/red) for performance levels
- **Responsive Design**: Works perfectly on desktop, tablet, and mobile
- **Expandable Sections**: Collapsible scorecard criteria for easy navigation
- **Real-time Filtering**: Instant results without page refreshes

### 📊 Data Architecture

- **Reverse Sync Pipeline**: Data synchronized from Databricks Delta Lake (Gold layer)
- **Lakehouse Integration**: Leverages Databricks for AI scoring and data processing
- **Autoscaling PostgreSQL**: High-performance Lakebase serving layer
- **JSONB Scorecards**: Flexible structured data storage for quality metrics

## Getting Started

1. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

2. Set up environment variables:

   - Copy `example.env` to `.env`
   - Fill in your actual Databricks credentials:
     - `DATABRICKS_HOST`
     - `DATABRICKS_CLIENT_ID`
     - `DATABRICKS_CLIENT_SECRET`
     - `LAKEBASE_INSTANCE_NAME`
     - `LAKEBASE_DB_NAME`

3. Run the application:

   ```bash
   python app.py
   ```

4. Open your browser to `http://localhost:8000`

## API Endpoints

### Call Analytics

- `GET /api/calls` - List all calls with optional filtering
  - Query parameters:
    - `member_id` (optional): Filter by member ID
    - `min_score` (optional): Filter calls with total_score >= value
    - `start_date` (optional): Filter calls on or after this date (YYYY-MM-DD)
    - `end_date` (optional): Filter calls on or before this date (YYYY-MM-DD)
- `GET /api/calls/{call_id}` - Get full details of a specific call (transcript + scorecard)

### System

- `GET /health` - Health check endpoint

## Database Architecture

### Lakebase Connection

- **Singleton Pattern**: Efficient connection pooling with automatic token refresh
- **OAuth Integration**: Seamless Databricks authentication
- **Token Refresh**: Automatic renewal every 59 minutes
- **Connection Pooling**: Optimized database connections

### Data Pipeline

The application reads from data that flows through this pipeline:

1. **Bronze Layer**: Raw call transcripts ingested into Delta Lake
2. **Silver Layer**: Cleaned and prepared data
3. **Gold Layer**: AI-scored data with quality assessments (source of truth)
4. **Reverse Sync**: Continuous synchronization to Lakebase PostgreSQL for serving

### Security Considerations

⚠️ **SECURITY WARNING**: This demo uses f-string SQL queries for simplicity. In production, always use parameterized queries to prevent SQL injection attacks.

## Database Schema

The application reads from the `public.analytics.call_center_scores_sync` table:

```sql
CREATE TABLE IF NOT EXISTS public.analytics.call_center_scores_sync (
    call_id TEXT PRIMARY KEY,
    member_id TEXT,
    call_date TEXT,
    transcript TEXT,
    scorecard_json JSONB,
    total_score INTEGER
);
```

### Scorecard Structure (scorecard_json JSONB)

```json
{
  "criteria_1": {
    "technical_aspects": {
      "recording_disclosure": {"score": 8},
      "member_authentication": {"score": 9},
      "call_closing": {"score": 7}
    }
  },
  "criteria_2": {
    "quality_of_service": {
      "professionalism": {"score": 9},
      "program_information": {"score": 8},
      "demeanor": {"score": 9}
    }
  },
  "total_score": 50
}
```

## Why These Technologies?

- **FastAPI**: Modern, fast, and type-safe Python web framework
- **Databricks Lakebase**: Autoscaling PostgreSQL serving layer that bridges Lakehouse and operational apps
- **Reverse Sync Pattern**: Maintains single source of truth in Delta Lake while providing low-latency access
- **JSONB**: Flexible storage for AI-generated structured data with efficient querying
