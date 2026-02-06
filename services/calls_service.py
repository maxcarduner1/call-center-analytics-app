"""
Service for managing call center data queries.

⚠️ SECURITY WARNING ⚠️
THIS SERVICE USES F-STRING SQL QUERIES INSTEAD OF PARAMETERIZED QUERIES.
THIS IS A SECURITY RISK AND MAKES THE APPLICATION VULNERABLE TO SQL INJECTION.
THIS IS ACCEPTABLE ONLY FOR DEMO PURPOSES - NEVER USE IN PRODUCTION!
"""
from typing import List, Tuple, Any, Optional
from services.lakebase import Lakebase
from services.human_evaluations_service import get_human_evaluation
import json


def list_calls(
    member_id: Optional[str] = None,
    min_score: Optional[int] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    call_center_rep_id: Optional[str] = None
) -> List[Tuple[Any, ...]]:
    """
    List all calls with optional filtering.
    
    Args:
        member_id: Filter by member ID
        min_score: Filter calls with total_score >= min_score
        start_date: Filter calls on or after this date (YYYY-MM-DD)
        end_date: Filter calls on or before this date (YYYY-MM-DD)
        call_center_rep_id: Filter by call center representative ID
    
    Returns:
        List of tuples containing (call_id, member_id, call_date, total_score, rep_id)
    """
    # Base query
    sql = """
        SELECT 
            call_id, 
            member_id, 
            call_date,
            call_time,
            total_score,
            rep_id
        FROM public.telco_call_center_analytics.call_center_scores_sync
    """
    
    # Build WHERE clauses
    where_clauses = []
    
    if member_id:
        where_clauses.append(f"member_id = '{member_id}'")
    
    if min_score is not None:
        where_clauses.append(f"total_score >= {min_score}")
    
    if start_date:
        where_clauses.append(f"call_date >= '{start_date}'")
    
    if end_date:
        where_clauses.append(f"call_date <= '{end_date} 23:59:59'")
    
    if call_center_rep_id:
        where_clauses.append(f"rep_id = '{call_center_rep_id}'")
    
    # Add WHERE clause if any filters
    if where_clauses:
        sql += " WHERE " + " AND ".join(where_clauses)
    
    # Order by most recent first
    sql += " ORDER BY call_date DESC"
    
    # Execute query
    lakebase = Lakebase()
    return lakebase.query(sql)


def get_call_by_id(call_id: str) -> Optional[Tuple[Any, ...]]:
    """
    Get full details of a specific call.
    
    Args:
        call_id: The call ID to retrieve
    
    Returns:
        Tuple containing (call_id, member_id, call_date, transcript, scorecard)
        or None if call not found
    """
    sql = f"SELECT * FROM public.telco_call_center_analytics.call_center_scores_sync WHERE call_id = '{call_id}'"
    
    lakebase = Lakebase()
    rows = lakebase.query(sql)
    
    if rows and len(rows) > 0:
        return rows[0]
    return None


def get_all_ccr_ids() -> List[Tuple[Any, ...]]:
    """
    Get list of all unique call center representative IDs.
    
    Returns:
        List of tuples containing (rep_id,)
    """
    sql = """
        SELECT DISTINCT rep_id 
        FROM public.telco_call_center_analytics.call_center_scores_sync 
        WHERE rep_id IS NOT NULL
        ORDER BY rep_id
    """
    
    lakebase = Lakebase()
    return lakebase.query(sql)


def get_ccr_aggregate_stats(call_center_rep_id: str) -> Optional[Tuple[Any, ...]]:
    """
    Get aggregate performance statistics for a specific call center representative.
    
    Args:
        call_center_rep_id: The call center rep ID to get stats for
    
    Returns:
        Tuple containing (rep_id, total_calls, avg_score, min_score, max_score)
        or None if no data found
    """
    sql = f"""
        SELECT 
            rep_id,
            COUNT(*) as total_calls,
            ROUND(AVG(total_score)::numeric, 2) as avg_score,
            MIN(total_score) as min_score,
            MAX(total_score) as max_score
        FROM public.telco_call_center_analytics.call_center_scores_sync
        WHERE rep_id = '{call_center_rep_id}'
        GROUP BY rep_id
    """
    
    lakebase = Lakebase()
    rows = lakebase.query(sql)
    
    if rows and len(rows) > 0:
        return rows[0]
    return None


def merge_ai_and_human_scores(call_data: dict) -> dict:
    """
    Merge AI scores with human overrides (if they exist).
    
    This function checks if a human evaluation exists for the call
    and merges it with the AI-generated scores, preferring human
    overrides where they exist.
    
    Args:
        call_data: Dictionary containing call information with AI scores
    
    Returns:
        Dictionary with merged scores and evaluation metadata
    """
    call_id = call_data.get("call_id")
    
    if not call_id:
        return call_data
    
    # Try to get human evaluation
    human_eval = get_human_evaluation(call_id)
    
    if human_eval is None:
        # No human evaluation, return AI scores as-is
        call_data["has_human_override"] = False
        return call_data
    
    # Parse human evaluation
    scorecard_overrides = human_eval[4] if len(human_eval) > 4 else {}
    if isinstance(scorecard_overrides, str):
        scorecard_overrides = json.loads(scorecard_overrides)
    
    total_score_override = human_eval[5] if len(human_eval) > 5 else None
    feedback_text = human_eval[6] if len(human_eval) > 6 else ""
    evaluator_name = human_eval[2] if len(human_eval) > 2 else None
    evaluation_date = human_eval[3] if len(human_eval) > 3 else None
    
    # Merge scores: human overrides take precedence
    if scorecard_overrides:
        # Deep merge the scorecard
        ai_scorecard = call_data.get("scorecard", {})
        merged_scorecard = deep_merge_scorecards(ai_scorecard, scorecard_overrides)
        call_data["scorecard"] = merged_scorecard
    
    # Override total score if provided
    if total_score_override is not None:
        call_data["total_score"] = total_score_override
    
    # Add evaluation metadata
    call_data["has_human_override"] = True
    call_data["human_evaluation"] = {
        "evaluator_name": evaluator_name,
        "evaluation_date": str(evaluation_date) if evaluation_date else None,
        "feedback_text": feedback_text,
        "scorecard_overrides": scorecard_overrides,
        "total_score_override": total_score_override
    }
    
    return call_data


def deep_merge_scorecards(ai_scorecard: dict, human_overrides: dict) -> dict:
    """
    Deep merge AI scorecard with human overrides.
    Human scores take precedence over AI scores.
    
    Args:
        ai_scorecard: Original AI-generated scorecard
        human_overrides: Human override scores
    
    Returns:
        Merged scorecard dictionary
    """
    merged = ai_scorecard.copy()
    
    for key, value in human_overrides.items():
        if isinstance(value, dict) and key in merged and isinstance(merged[key], dict):
            # Recursively merge nested dictionaries
            merged[key] = deep_merge_scorecards(merged[key], value)
        else:
            # Override with human value
            merged[key] = value
    
    return merged
