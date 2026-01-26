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
    end_date: Optional[str] = None
) -> List[Tuple[Any, ...]]:
    """
    List all calls with optional filtering.
    
    Args:
        member_id: Filter by member ID
        min_score: Filter calls with total_score >= min_score
        start_date: Filter calls on or after this date (YYYY-MM-DD)
        end_date: Filter calls on or before this date (YYYY-MM-DD)
    
    Returns:
        List of tuples containing (call_id, member_id, call_date, total_score)
    """
    # Base query
    sql = """
        SELECT 
            call_id, 
            member_id, 
            call_date, 
            total_score 
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
