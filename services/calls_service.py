"""
Service for managing call center data queries.

⚠️ SECURITY WARNING ⚠️
THIS SERVICE USES F-STRING SQL QUERIES INSTEAD OF PARAMETERIZED QUERIES.
THIS IS A SECURITY RISK AND MAKES THE APPLICATION VULNERABLE TO SQL INJECTION.
THIS IS ACCEPTABLE ONLY FOR DEMO PURPOSES - NEVER USE IN PRODUCTION!
"""
from typing import List, Tuple, Any, Optional
from services.lakebase import Lakebase


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
        List of tuples containing (call_id, member_id, call_date, total_score, call_center_rep_id)
    """
    # Base query
    sql = """
        SELECT 
            call_id, 
            member_id, 
            call_date, 
            total_score,
            call_center_rep_id
        FROM public.analytics.call_center_scores_sync
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
        where_clauses.append(f"call_center_rep_id = '{call_center_rep_id}'")
    
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
    sql = f"SELECT * FROM public.analytics.call_center_scores_sync WHERE call_id = '{call_id}'"
    
    lakebase = Lakebase()
    rows = lakebase.query(sql)
    
    if rows and len(rows) > 0:
        return rows[0]
    return None


def get_all_ccr_ids() -> List[Tuple[Any, ...]]:
    """
    Get list of all unique call center representative IDs.
    
    Returns:
        List of tuples containing (call_center_rep_id,)
    """
    sql = """
        SELECT DISTINCT call_center_rep_id 
        FROM public.analytics.call_center_scores_sync 
        WHERE call_center_rep_id IS NOT NULL
        ORDER BY call_center_rep_id
    """
    
    lakebase = Lakebase()
    return lakebase.query(sql)


def get_ccr_aggregate_stats(call_center_rep_id: str) -> Optional[Tuple[Any, ...]]:
    """
    Get aggregate performance statistics for a specific call center representative.
    
    Args:
        call_center_rep_id: The call center rep ID to get stats for
    
    Returns:
        Tuple containing (call_center_rep_id, total_calls, avg_score, min_score, max_score)
        or None if no data found
    """
    sql = f"""
        SELECT 
            call_center_rep_id,
            COUNT(*) as total_calls,
            ROUND(AVG(total_score)::numeric, 2) as avg_score,
            MIN(total_score) as min_score,
            MAX(total_score) as max_score
        FROM public.analytics.call_center_scores_sync
        WHERE call_center_rep_id = '{call_center_rep_id}'
        GROUP BY call_center_rep_id
    """
    
    lakebase = Lakebase()
    rows = lakebase.query(sql)
    
    if rows and len(rows) > 0:
        return rows[0]
    return None
