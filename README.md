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

- **All Calls View**: Browse all call center transcripts with key metrics
  - Filter by member ID, date range, minimum score, and call center rep
  - View quality scores for all calls
  - Quick access to detailed scorecards
  - See which calls have been reviewed by humans (✏️ REVIEWED badge)
- **CCR View**: Dedicated view for call center representative performance
  - Select specific call center representative
  - View aggregate performance statistics (total calls, avg/min/max scores)
  - See all calls for that representative in one place
  - View human-reviewed scores for each call
- **Human Evaluation & Override**: Quality assurance workflow
  - Override AI-generated scores with human expert review
  - Edit individual scorecard criteria
  - Add free-form feedback and notes
  - Track who reviewed each call and when
  - Delete evaluations to revert to AI scores
  - Human scores automatically displayed throughout the app
- **Quality Scores**: View AI-generated quality scores for each call (0-60 scale)
- **Detailed Scorecards**: Drill down into specific scoring criteria:
  - Technical Aspects (Recording Disclosure, Member Authentication, Call Closing)
  - Quality of Service (Professionalism, Program Information, Demeanor)
- **Full Transcripts**: Read complete call transcripts
- **Advanced Filtering**: Filter calls by member ID, date range, minimum score, and call center rep

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

4. Initialize the human evaluations table (first-time setup):

   ```bash
   curl -X POST http://localhost:8000/api/evaluations/init-table
   ```

5. Open your browser to `http://localhost:8000`

## API Endpoints

### Call Analytics

- `GET /api/calls` - List all calls with optional filtering
  - Query parameters:
    - `member_id` (optional): Filter by member ID
    - `min_score` (optional): Filter calls with total_score >= value
    - `start_date` (optional): Filter calls on or after this date (YYYY-MM-DD)
    - `end_date` (optional): Filter calls on or before this date (YYYY-MM-DD)
    - `call_center_rep_id` (optional): Filter by call center representative ID
- `GET /api/calls/{call_id}` - Get full details of a specific call (transcript + scorecard)

### Call Center Representatives

- `GET /api/ccrs` - Get list of all call center representative IDs
- `GET /api/ccrs/{ccr_id}/stats` - Get aggregate performance statistics for a specific CCR
  - Returns: total_calls, avg_score, min_score, max_score

### Human Evaluations

- `POST /api/evaluations/init-table` - Initialize human evaluations table (one-time setup)
- `GET /api/evaluations/{call_id}` - Get human evaluation for a specific call
- `POST /api/evaluations/{call_id}` - Save or update human evaluation
  - Body: `{ evaluator_name, scorecard_overrides, total_score_override, feedback_text }`
- `DELETE /api/evaluations/{call_id}` - Delete human evaluation (revert to AI scores)
- `GET /api/evaluations/` - Get list of all call IDs with human evaluations

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

### Call Center Scores (AI-Generated)

The application reads AI-generated scores from the `public.analytics.call_center_scores_sync` table:

```sql
CREATE TABLE IF NOT EXISTS public.analytics.call_center_scores_sync (
    call_id TEXT PRIMARY KEY,
    member_id TEXT,
    call_date TEXT,
    transcript TEXT,
    scorecard_json JSONB,
    total_score INTEGER,
    call_center_rep_id TEXT,
    transcript_summary TEXT
);
```

**Note:** This table is continuously synced from Databricks Delta Lake. Do not modify directly.

**Fields:**
- `transcript_summary`: AI-generated summary of the call, displayed in the call detail view between the quality score and full transcript

### Human Evaluations (Override Scores)

Human evaluations are stored separately in `public.analytics.human_evaluations`:

```sql
CREATE TABLE IF NOT EXISTS public.analytics.human_evaluations (
    evaluation_id SERIAL PRIMARY KEY,
    call_id TEXT NOT NULL UNIQUE,
    evaluator_name TEXT,
    evaluation_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    scorecard_overrides JSONB,
    total_score_override INTEGER,
    feedback_text TEXT
);
```

**Data Flow:**
1. AI scores remain in `call_center_scores_sync` (source of truth from ETL)
2. Human overrides stored in `human_evaluations` (this app writes here)
3. Application merges both at query time, preferring human scores when they exist
4. UI clearly indicates when scores have been human-reviewed

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
