"""
Service for managing human evaluations and score overrides.

This service handles storing and retrieving human evaluations that override
AI-generated scores. Human evaluations are stored separately to preserve the
original AI scores while allowing reviewers to provide corrected assessments.

⚠️ SECURITY WARNING ⚠️
THIS SERVICE USES F-STRING SQL QUERIES INSTEAD OF PARAMETERIZED QUERIES.
THIS IS A SECURITY RISK AND MAKES THE APPLICATION VULNERABLE TO SQL INJECTION.
THIS IS ACCEPTABLE ONLY FOR DEMO PURPOSES - NEVER USE IN PRODUCTION!

Database Schema:
----------------
CREATE TABLE IF NOT EXISTS public.telco_call_center_analytics.human_evaluations (
    evaluation_id SERIAL PRIMARY KEY,
    call_id TEXT NOT NULL,
    evaluator_name TEXT,
    evaluation_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    scorecard_overrides JSONB,
    total_score_override INTEGER,
    feedback_text TEXT,
    UNIQUE(call_id)
);

The scorecard_overrides JSONB follows the same structure as scorecard_json:
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
  }
}
"""
from typing import List, Tuple, Any, Optional
from services.lakebase import Lakebase
import json


def ensure_human_evaluations_table():
    """
    Ensure the human_evaluations table exists.
    This should be called on application startup.
    """
    sql = """
        CREATE TABLE IF NOT EXISTS public.telco_call_center_analytics.human_evaluations (
            evaluation_id SERIAL PRIMARY KEY,
            call_id TEXT NOT NULL,
            evaluator_name TEXT,
            evaluation_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            scorecard_overrides JSONB,
            total_score_override INTEGER,
            feedback_text TEXT,
            UNIQUE(call_id)
        ) RETURNING *
    """
    
    lakebase = Lakebase()
    return lakebase.query(sql)


def get_human_evaluation(call_id: str) -> Optional[Tuple[Any, ...]]:
    """
    Get human evaluation for a specific call.
    
    Args:
        call_id: The call ID to retrieve evaluation for
    
    Returns:
        Tuple containing (evaluation_id, call_id, evaluator_name, evaluation_date,
                         scorecard_overrides, total_score_override, feedback_text)
        or None if no evaluation exists
    """
    sql = f"""
        SELECT 
            evaluation_id, 
            call_id, 
            evaluator_name, 
            evaluation_date,
            scorecard_overrides, 
            total_score_override, 
            feedback_text
        FROM public.telco_call_center_analytics.human_evaluations 
        WHERE call_id = '{call_id}'
    """
    
    lakebase = Lakebase()
    rows = lakebase.query(sql)
    
    if rows and len(rows) > 0:
        return rows[0]
    return None


def save_human_evaluation(
    call_id: str,
    evaluator_name: str,
    scorecard_overrides: dict,
    total_score_override: int,
    feedback_text: str = ""
) -> Tuple[Any, ...]:
    """
    Save or update a human evaluation for a call.
    
    Args:
        call_id: The call ID being evaluated
        evaluator_name: Name of the person doing the evaluation
        scorecard_overrides: Dictionary with override scores (same structure as scorecard_json)
        total_score_override: Total override score (0-60)
        feedback_text: Free-form text feedback
    
    Returns:
        Tuple containing the saved evaluation row
    """
    # Convert scorecard to JSON string
    scorecard_json = json.dumps(scorecard_overrides).replace("'", "''")
    feedback_escaped = feedback_text.replace("'", "''")
    evaluator_escaped = evaluator_name.replace("'", "''")
    
    sql = f"""
        INSERT INTO public.telco_call_center_analytics.human_evaluations 
            (call_id, evaluator_name, scorecard_overrides, total_score_override, feedback_text)
        VALUES 
            ('{call_id}', '{evaluator_escaped}', '{scorecard_json}'::jsonb, {total_score_override}, '{feedback_escaped}')
        ON CONFLICT (call_id) 
        DO UPDATE SET
            evaluator_name = EXCLUDED.evaluator_name,
            evaluation_date = CURRENT_TIMESTAMP,
            scorecard_overrides = EXCLUDED.scorecard_overrides,
            total_score_override = EXCLUDED.total_score_override,
            feedback_text = EXCLUDED.feedback_text
        RETURNING *
    """
    
    lakebase = Lakebase()
    rows = lakebase.query(sql)
    
    if rows and len(rows) > 0:
        return rows[0]
    return None


def delete_human_evaluation(call_id: str) -> bool:
    """
    Delete a human evaluation for a call.
    
    Args:
        call_id: The call ID to delete evaluation for
    
    Returns:
        True if deleted, False if not found
    """
    sql = f"""
        DELETE FROM public.telco_call_center_analytics.human_evaluations 
        WHERE call_id = '{call_id}'
        RETURNING *
    """
    
    lakebase = Lakebase()
    rows = lakebase.query(sql)
    
    return rows and len(rows) > 0


def get_all_evaluated_call_ids() -> List[str]:
    """
    Get list of all call IDs that have human evaluations.
    
    Returns:
        List of call IDs
    """
    sql = """
        SELECT call_id 
        FROM public.telco_call_center_analytics.human_evaluations
        ORDER BY evaluation_date DESC
    """
    
    lakebase = Lakebase()
    rows = lakebase.query(sql)
    
    return [row[0] for row in rows if row[0]]
