"""
================================================================================
SENSOR SIMULATOR - MACHINE SENSOR DATA SIMULATION
================================================================================

This module simulates real-time sensor data from manufacturing machines.

WHAT IT DOES:
- Generates realistic sensor readings (temperature, vibration, pressure, RPM).
- Simulates normal operational fluctuations.
- Allows triggering fault conditions for testing/demos.

WHY SIMULATION?
- No need for real industrial equipment for development.
- Demonstrates the system's sensor monitoring capabilities.
- Allows controlled testing of fault detection.
- In production, this would be replaced with actual PLC/SCADA integration.

HOW IT WORKS:
1. Maintains internal state for each machine's sensors.
2. On each call to get_readings():
   - Applies small random fluctuations (simulating normal operation).
   - Uses sine waves for realistic vibration patterns.
   - Clamps values to realistic ranges.
3. trigger_fault() modifies state to simulate specific fault conditions.

BIG PICTURE:
- Powers the "Sensor Dashboard" in the frontend.
- Provides data for the DIAGNOSTICS agent's analysis.
- Enables end-to-end testing without real sensors.

FUTURE ENHANCEMENTS:
- Replace with OPC-UA/Modbus integration for real PLCs.
- Add historical data storage for trend analysis.
- Implement anomaly detection algorithms.

ARCHITECTURE:
    [Sensors API / Orchestrator]
              |
              v
    [Sensor Simulator]  <-- YOU ARE HERE
              |
              ├── get_readings() --> Current sensor values
              |
              └── trigger_fault() --> Inject test faults
================================================================================
"""

import random
import time
import math
from typing import Dict


class SensorSimulator:
    """
    Simulates sensor readings for multiple manufacturing machines.
    
    Maintains internal state that evolves over time with realistic
    fluctuations and allows fault injection for testing.
    
    Attributes:
        machines: List of machine IDs being simulated.
        state: Dictionary of current sensor states per machine.
    """
    
    def __init__(self):
        """
        Initialize the simulator with default machine states.
        
        Creates three simulated machines with nominal sensor values.
        """
        # Machine IDs (would come from plant database in production)
        self.machines = ["CNC-204", "PRESS-505", "ROBOT-101"]
        
        # Initialize each machine with nominal operating values
        self.state = {
            m: {
                "temperature": 45.0,    # °C (normal: 40-70)
                "vibration": 0.5,       # mm/s (normal: < 1.0)
                "rpm": 1200,            # Revolutions per minute
                "pressure": 100.0,      # PSI (normal: 90-110)
                "status": "Running"     # Operating status
            } for m in self.machines
        }
    
    def get_readings(self) -> Dict[str, Dict]:
        """
        Get current sensor readings for all machines.
        
        WHAT: Returns simulated sensor data with realistic fluctuations.
        HOW: Applies random noise and mathematical patterns to base values.
        BIG PICTURE: Called by /sensors endpoint and DIAGNOSTICS agent.
        
        Simulation Details:
        - Temperature: Random walk with ±0.5°C per reading.
        - Vibration: Sine wave + random noise for realistic oscillation.
        - RPM: Small integer variations around 1200.
        - Pressure: Random fluctuations within normal range.
        
        Returns:
            Dict[str, Dict]: Machine ID -> sensor readings.
        """
        current_time = time.time()
        
        for machine in self.machines:
            # =========================================================
            # TEMPERATURE SIMULATION
            # Random walk: each reading adds/subtracts a small amount.
            # This simulates gradual heating/cooling during operation.
            # =========================================================
            self.state[machine]["temperature"] += random.uniform(-0.5, 0.5)
            
            # =========================================================
            # VIBRATION SIMULATION
            # Combines sine wave (periodic mechanical vibration) with
            # random noise (irregularities). More realistic than pure random.
            # =========================================================
            self.state[machine]["vibration"] = 0.5 + 0.2 * math.sin(current_time) + random.uniform(-0.05, 0.05)
            
            # =========================================================
            # RPM SIMULATION
            # Small integer variations around nominal 1200 RPM.
            # =========================================================
            self.state[machine]["rpm"] = 1200 + random.randint(-10, 10)
            
            # =========================================================
            # PRESSURE SIMULATION
            # Random fluctuations within ±1 PSI of nominal.
            # =========================================================
            self.state[machine]["pressure"] = 100.0 + random.uniform(-1, 1)

            # Clamp temperature to realistic bounds (prevent runaway values)
            self.state[machine]["temperature"] = max(20, min(150, self.state[machine]["temperature"]))
        
        return self.state

    def trigger_fault(self, machine_id: str, fault_type: str):
        """
        Inject a fault condition into a machine's sensors.
        
        WHAT: Simulates a specific fault for testing/demo purposes.
        HOW: Sets sensor values and status to fault levels.
        BIG PICTURE: Used to test DIAGNOSTICS agent's fault detection.
        
        Supported Fault Types:
        - overheat: Temperature spikes to 110°C
        - vibration: Vibration spikes to 2.5 mm/s (critical)
        - pressure_loss: Pressure drops to 20 PSI
        
        Args:
            machine_id: Which machine to apply the fault to.
            fault_type: Type of fault to simulate.
            
        Returns:
            dict: Confirmation message and new machine state.
        """
        if machine_id not in self.machines:
            return {"error": "Machine not found"}
        
        # Apply fault based on type
        if fault_type == "overheat":
            self.state[machine_id]["temperature"] = 110.0
            self.state[machine_id]["status"] = "Warning"
        elif fault_type == "vibration":
            self.state[machine_id]["vibration"] = 2.5
            self.state[machine_id]["status"] = "Critical"
        elif fault_type == "pressure_loss":
            self.state[machine_id]["pressure"] = 20.0
            self.state[machine_id]["status"] = "Warning"
        
        return {"message": f"Fault {fault_type} triggered on {machine_id}", "state": self.state[machine_id]}


# Global singleton instance
# Maintains state across API calls
simulator = SensorSimulator()

