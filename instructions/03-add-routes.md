# Fill in the details

Make the app into a Call Quality Scoring viewer with these specifications.
Do not be fancy with parameterization, just use f-strings.
Make the UI look crisp - minimalistic yet aesthetically pleasing with a professional call center dashboard feel.

## Database Table

The application reads from the `call_center_scores_sync` table in the `telco_call_center_analytics` schema, which is synchronized from Databricks via the reverse sync pipeline described in the design document.

**Schema**: `public.telco_call_center_analytics`

## Frontend & User Experience

The application should have two main views:

### 1. Call List View (Homepage)
- Display a table/list of all calls showing:
  - Call ID
  - Member ID  
  - Call Date (formatted nicely)
  - Total Score (with visual indicator - green for high scores, yellow for medium, red for low)
- Each row should be clickable to view the full call details
- Include filtering options:
  - Filter by member ID (text input)
  - Filter by date range (from/to date pickers)
  - Filter by minimum score (number input)
- Show call count at the top

### 2. Call Detail View
When a call is clicked, show:
- Call metadata at the top (Call ID, Member ID, Call Date)
- Full transcript in a readable, scrollable section
- Detailed scorecard breakdown showing:
  - **Criteria 1: Technical Aspects** (expandable section)
    - Recording Disclosure: score/10
    - Member Authentication: score/10
    - Call Closing: score/10
  - **Criteria 2: Quality of Service** (expandable section)
    - Professionalism: score/10
    - Program Information: score/10
    - Demeanor: score/10
  - **Total Score** prominently displayed
- Use color coding (green/yellow/red) for individual scores
- "Back to List" button to return to the homepage

Use HTML's modern features and make it responsive.

**Remove the test lakebase button from the UI, and remove the associated test endpoint.**

## Backend

### Required Routes

Create these API endpoints:

- **GET** `/calls` - List all calls with optional filtering
  - Query parameters:
    - `member_id` (optional): Filter by member ID
    - `min_score` (optional): Filter calls with total_score >= min_score
    - `start_date` (optional): Filter calls on or after this date
    - `end_date` (optional): Filter calls on or before this date
- **GET** `/calls/{call_id}` - Get full details of a specific call (transcript + scorecard)

### Architecture

Implement router/controller pattern. Move routes to `/routers/calls.py` and keep `app.py` clean.
Add this router to app.py.

#### calls-service

Create a `calls_service.py` in the `/services` folder that exposes functions:

- `list_calls(member_id=None, min_score=None, start_date=None, end_date=None)` - Returns list of calls with filtering
- `get_call_by_id(call_id)` - Returns full call details including transcript and scorecard

**SECURITY WARNING**: Use simple f-strings for SQL queries instead of parameterized queries. This is less safe for production but acceptable for this demo. **CALL OUT TO ME IN ALL CAPS WHEN YOU IMPLEMENT THIS SO I REMEMBER THE SECURITY TRADEOFF.**

The table is located at `public.telco_call_center_analytics.call_center_scores_sync`.

### Database Schema

This is the structure of the table (synchronized from Databricks). You can assume it's already been created and populated.

```sql
CREATE TABLE IF NOT EXISTS public.telco_call_center_analytics.call_center_scores_sync (
    call_id TEXT PRIMARY KEY,
    member_id TEXT,
    rep_id TEXT,
    rep_name TEXT,
    call_date TEXT,
    call_time TEXT,
    call_outcome TEXT,
    call_purpose TEXT,
    call_duration_seconds INTEGER,
    transcript TEXT,
    scorecard_json JSONB,
    total_score INTEGER,
    transcript_summary TEXT
);
```

**Field Notes:**
- `transcript_summary`: AI-generated summary of the call conversation, should be displayed in the call detail view

The `scorecard_json` JSONB column has this structure:

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

### Service Implementation Notes

For `list_calls()`:
- Base query: `SELECT call_id, member_id, call_date, total_score FROM public.telco_call_center_analytics.call_center_scores_sync`
- Add WHERE clauses dynamically based on provided filters
- Order by call_date DESC (most recent first)
- The total_score is already an integer column (no need to extract from JSONB)

For `get_call_by_id()`:
- Query: `SELECT * FROM public.telco_call_center_analytics.call_center_scores_sync WHERE call_id = '{call_id}'`
- Return the full row including transcript and complete scorecard_json JSONB
- Return None if call_id not found

Both functions should use `Lakebase.query()` and return rows as-is (lists of tuples).
