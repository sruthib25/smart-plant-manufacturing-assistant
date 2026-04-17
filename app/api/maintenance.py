"""
================================================================================
MAINTENANCE API - INVENTORY AND LOG ANALYSIS ENDPOINTS
================================================================================

This module provides REST API endpoints for maintenance-related features.

WHAT IT DOES:
- Manages spare parts inventory access.
- Triggers scarcity alerts for parts.
- Analyzes uploaded CSV log files with AI.

ENDPOINTS:
- GET /maintenance/inventory   : Get spare parts list.
- POST /maintenance/alert      : Report part scarcity.
- POST /maintenance/analyze-log : Analyze a machine log file.

HOW IT WORKS:
1. Inventory: Returns mock data from InventoryService.
2. Alerts: Simulates notification (would send email in production).
3. Log Analysis:
   - Uploads CSV file via multipart form.
   - Parses with Pandas to generate statistics.
   - Uses LLM to generate a performance report.

BIG PICTURE:
- Enables the "Maintenance" tab in the frontend.
- Provides predictive maintenance capabilities via log analysis.
- Helps prevent production downtime from parts shortages.

ARCHITECTURE:
    [Frontend Maintenance UI]
              |
              v (HTTP)
    [Maintenance API]  <-- YOU ARE HERE
              |
    +---------+---------+
    |         |         |
    v         v         v
  Inventory  Alert    Log Analysis
  Service   (SMTP)    (Pandas + LLM)
================================================================================
"""

from fastapi import APIRouter, UploadFile, File, HTTPException
from pydantic import BaseModel
import pandas as pd
import io
from app.services.inventory_service import inventory_service
from app.services.llm_service import llm_service

# Create router with /maintenance prefix
# All endpoints in this file start with /maintenance/
router = APIRouter(prefix="/maintenance", tags=["Maintenance"])


@router.get("/inventory")
async def get_inventory():
    """
    Get the spare parts inventory.
    
    WHAT: Returns list of all spare parts with stock levels.
    HOW: Queries InventoryService for parts data.
    BIG PICTURE: Powers the "Spare Parts" table in the frontend.
    
    Returns:
        {"inventory": [{"id": "p1", "name": "Part Name", "stock": 5, ...}, ...]}
    """
    return {"inventory": inventory_service.get_inventory()}


class AlertRequest(BaseModel):
    """
    Request model for scarcity alerts.
    
    Attributes:
        part_name: Name of the part that is scarce.
        machine_id: ID of the machine that needs the part.
    """
    part_name: str
    machine_id: str


@router.post("/alert")
async def trigger_alert(request: AlertRequest):
    """
    Trigger a scarcity alert for a spare part.
    
    WHAT: Notifies management about a part shortage.
    HOW: Calls InventoryService.trigger_scarcity_alert().
    BIG PICTURE: Called when user clicks "Report Scarcity" button.
    
    In production, this would send an email or create a purchase order.
    
    Args:
        request: AlertRequest with part_name and machine_id.
        
    Returns:
        {"status": "success", "message": "Alert sent to management for {part_name}."}
    """
    return inventory_service.trigger_scarcity_alert(request.part_name, request.machine_id)


@router.post("/analyze-log")
async def analyze_log(file: UploadFile = File(...)):
    """
    Analyze a machine log CSV file with AI.
    
    WHAT: Parses a CSV file and generates a performance report.
    HOW:
        1. Reads uploaded file as CSV using Pandas.
        2. Generates statistical summary (describe()).
        3. Sends summary to LLM for analysis.
        4. Returns both stats and AI-generated report.
    BIG PICTURE: Enables predictive maintenance by identifying anomalies.
    
    Args:
        file: Uploaded CSV file (multipart/form-data).
        
    Returns:
        {
            "stats": {...statistical summary from pandas...},
            "report": "AI-generated performance analysis..."
        }
        
    Raises:
        HTTPException 400: If CSV parsing fails.
    """
    try:
        # Read file content
        content = await file.read()
        
        # Parse CSV into DataFrame
        df = pd.read_csv(io.BytesIO(content))
        
        # =================================================================
        # GENERATE STATISTICS
        # Pandas describe() provides: count, mean, std, min, 25%, 50%, 75%, max
        # =================================================================
        stats = df.describe().to_dict()
        
        # =================================================================
        # PREPARE CONTEXT FOR LLM
        # Give the AI a summary of the data to analyze
        # =================================================================
        summary_str = df.describe().to_string()
        columns_str = ", ".join(df.columns)
        head_str = df.head().to_string()
        
        # =================================================================
        # LLM ANALYSIS PROMPT
        # Ask the AI to analyze the data and provide recommendations
        # =================================================================
        prompt = f"""Analyze the following machine log data and provide a performance report.
        
        Data Columns: {columns_str}
        Statistical Summary:
        {summary_str}
        
        First 5 rows:
        {head_str}
        
        Please provide:
        1. An assessment of machine stability.
        2. Any anomalies or concerns based on the stats (e.g., high variance, extreme min/max).
        3. Recommendations for maintenance.
        """
        
        # Generate AI report
        report = llm_service.generate(prompt)
        
        return {
            "stats": stats,
            "report": report
        }
        
    except Exception as e:
        # Return helpful error message if parsing fails
        raise HTTPException(status_code=400, detail=f"Error processing CSV: {str(e)}")

