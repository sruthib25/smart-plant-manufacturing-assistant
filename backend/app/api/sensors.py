"""
================================================================================
SENSORS API - MACHINE SENSOR DATA ENDPOINTS
================================================================================

This module provides REST API endpoints for sensor data access.

WHAT IT DOES:
- Returns current sensor readings for all machines.
- Allows triggering fault conditions for testing.

ENDPOINTS:
- GET /sensors  : Get current sensor readings for all machines.
- POST /fault   : Trigger a simulated fault on a specific machine.

HOW IT WORKS:
- Uses the SensorSimulator service to generate realistic data.
- Each call to GET /sensors returns updated (slightly varied) values.
- POST /fault injects specific fault conditions for testing.

BIG PICTURE:
- Powers the "Sensor Dashboard" in the frontend.
- Provides data for the DIAGNOSTICS agent.
- Enables testing of fault detection capabilities.

ARCHITECTURE:
    [Frontend Dashboard / Diagnostics Agent]
                 |
                 v (HTTP GET/POST)
    [Sensors API]  <-- YOU ARE HERE
                 |
                 v
    [Sensor Simulator Service]
================================================================================
"""

from fastapi import APIRouter
from app.services.simulator import simulator
from pydantic import BaseModel

# Create router instance for sensor-related endpoints
router = APIRouter()


class FaultRequest(BaseModel):
    """
    Request model for triggering a fault.
    
    Attributes:
        machine_id: ID of the machine to fault (e.g., "CNC-204").
        fault_type: Type of fault to simulate ("overheat", "vibration", "pressure_loss").
    """
    machine_id: str
    fault_type: str


@router.get("/sensors")
async def get_sensors():
    """
    Get current sensor readings for all machines.
    
    WHAT: Returns real-time (simulated) sensor data.
    HOW: Calls simulator.get_readings() which generates realistic values.
    BIG PICTURE: Powers the dashboard and diagnostics agent.
    
    Returns:
        {
            "CNC-204": {"temperature": 45.2, "vibration": 0.5, ...},
            "PRESS-505": {...},
            ...
        }
    """
    return simulator.get_readings()


@router.post("/fault")
async def trigger_fault(request: FaultRequest):
    """
    Trigger a simulated fault on a machine.
    
    WHAT: Injects a fault condition for testing.
    HOW: Calls simulator.trigger_fault() to modify sensor values.
    BIG PICTURE: Used to test the DIAGNOSTICS agent's fault detection.
    
    Args:
        request: FaultRequest with machine_id and fault_type.
        
    Returns:
        {"message": "Fault triggered", "state": {...updated sensor values...}}
    """
    return simulator.trigger_fault(request.machine_id, request.fault_type)

