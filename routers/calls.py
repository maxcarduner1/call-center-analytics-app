"""
Router for call center analytics endpoints.
"""
from fastapi import APIRouter, Query, HTTPException
from typing import Optional
import json

from services.calls_service import list_calls, get_call_by_id

router = APIRouter(prefix="/api", tags=["calls"])


@router.get("/calls")
async def get_calls(
    member_id: Optional[str] = Query(None, description="Filter by member ID"),
    min_score: Optional[int] = Query(None, description="Minimum total score"),
    start_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD)")
):
    """
    List all calls with optional filtering.
    """
    try:
        rows = list_calls(
            member_id=member_id,
            min_score=min_score,
            start_date=start_date,
            end_date=end_date
        )
        
        # Convert rows to list of dicts
        calls = []
        for row in rows:
            calls.append({
                "call_id": row[0],
                "member_id": row[1],
                "call_date": str(row[2]) if row[2] else None,
                "total_score": row[3]
            })
        
        return {
            "count": len(calls),
            "calls": calls
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/calls/{call_id}")
async def get_call(call_id: str):
    """
    Get full details of a specific call including transcript and scorecard.
    """
    try:
        row = get_call_by_id(call_id)
        
        if row is None:
            raise HTTPException(status_code=404, detail="Call not found")
        
        # Parse the scorecard JSON
        scorecard_json = row[4] if len(row) > 4 else {}
        if isinstance(scorecard_json, str):
            scorecard_json = json.loads(scorecard_json)
        
        return {
            "call_id": row[0],
            "member_id": row[1],
            "call_date": row[2],
            "transcript": row[3],
            "scorecard": scorecard_json,
            "total_score": row[5] if len(row) > 5 else None
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
