"""
Router for call center analytics endpoints.
"""
from fastapi import APIRouter, Query, HTTPException
from typing import Optional
import json

from services.calls_service import list_calls, get_call_by_id, get_all_ccr_ids, get_ccr_aggregate_stats

router = APIRouter(prefix="/api", tags=["calls"])


@router.get("/calls")
async def get_calls(
    member_id: Optional[str] = Query(None, description="Filter by member ID"),
    min_score: Optional[int] = Query(None, description="Minimum total score"),
    start_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD)"),
    call_center_rep_id: Optional[str] = Query(None, description="Filter by call center rep ID")
):
    """
    List all calls with optional filtering.
    """
    try:
        rows = list_calls(
            member_id=member_id,
            min_score=min_score,
            start_date=start_date,
            end_date=end_date,
            call_center_rep_id=call_center_rep_id
        )
        
        # Convert rows to list of dicts
        calls = []
        for row in rows:
            calls.append({
                "call_id": row[0],
                "member_id": row[1],
                "call_date": str(row[2]) if row[2] else None,
                "total_score": row[3],
                "call_center_rep_id": row[4] if len(row) > 4 else None
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
            "total_score": row[5] if len(row) > 5 else None,
            "call_center_rep_id": row[6] if len(row) > 6 else None
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/ccrs")
async def get_ccrs():
    """
    Get list of all call center representative IDs.
    """
    try:
        rows = get_all_ccr_ids()
        
        # Convert rows to list of CCR IDs
        ccr_ids = [row[0] for row in rows if row[0] is not None]
        
        return {
            "count": len(ccr_ids),
            "ccr_ids": ccr_ids
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/ccrs/{ccr_id}/stats")
async def get_ccr_stats(ccr_id: str):
    """
    Get aggregate performance statistics for a specific call center representative.
    """
    try:
        row = get_ccr_aggregate_stats(ccr_id)
        
        if row is None:
            raise HTTPException(status_code=404, detail="CCR not found or has no calls")
        
        return {
            "call_center_rep_id": row[0],
            "total_calls": row[1],
            "avg_score": float(row[2]) if row[2] is not None else None,
            "min_score": row[3],
            "max_score": row[4]
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
