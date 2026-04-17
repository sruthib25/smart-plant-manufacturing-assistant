"""
================================================================================
INVENTORY SERVICE - SPARE PARTS MANAGEMENT
================================================================================

This module manages spare parts inventory for the manufacturing plant.

WHAT IT DOES:
- Provides mock spare parts inventory data.
- Tracks stock levels per machine.
- Triggers scarcity alerts (simulates email notifications).

HOW IT WORKS:
- Stores inventory as a list of dictionaries (mock data).
- Each part has: id, machine_id, name, stock, min_stock.
- When scarcity is triggered, logs an alert (real app would send email).

BIG PICTURE:
- Enables the "Spare Parts & Maintenance" tab in the frontend.
- Helps operators track what parts are running low.
- Alerts can prevent production downtime from missing parts.

FUTURE ENHANCEMENTS:
- Connect to actual inventory management system (ERP).
- Real email/SMS notifications via SMTP/Twilio.
- Automatic reorder triggers when stock < min_stock.

ARCHITECTURE:
    [Maintenance API]
           |
           v
    [Inventory Service]  <-- YOU ARE HERE
           |
           ├── get_inventory() --> List of parts
           |
           └── trigger_scarcity_alert() --> Simulated notification
================================================================================
"""

from typing import List, Dict


class InventoryService:
    """
    Service for managing spare parts inventory.
    
    In a production system, this would connect to an ERP/inventory database.
    Currently uses mock data for demonstration purposes.
    
    Attributes:
        inventory: List of spare parts with stock information.
    """
    
    def __init__(self):
        """
        Initialize with mock inventory data.
        
        Each inventory item contains:
        - id: Unique identifier for the part
        - machine_id: Which machine this part belongs to
        - name: Human-readable name of the part
        - stock: Current quantity in stock
        - min_stock: Minimum stock level (below = reorder needed)
        """
        self.inventory = [
            # Machine m1 parts
            {"id": "p1", "machine_id": "m1", "name": "Bearing Unit 204", "stock": 5, "min_stock": 2},
            {"id": "p2", "machine_id": "m1", "name": "Hydraulic Seal Kit", "stock": 2, "min_stock": 3},  # Low stock!
            # Machine m2 parts
            {"id": "p3", "machine_id": "m2", "name": "Vibration Sensor Type-A", "stock": 8, "min_stock": 2},
            {"id": "p4", "machine_id": "m2", "name": "Conveyor Belt Link", "stock": 50, "min_stock": 20},
            # Machine m3 parts
            {"id": "p5", "machine_id": "m3", "name": "Control Panel Fuse 10A", "stock": 0, "min_stock": 5},  # Out of stock!
        ]

    def get_inventory(self) -> List[Dict]:
        """
        Get the full inventory list.
        
        WHAT: Returns all spare parts and their stock levels.
        HOW: Returns the internal inventory list.
        BIG PICTURE: Called by GET /maintenance/inventory endpoint.
        
        Returns:
            List[Dict]: List of inventory items.
        """
        return self.inventory

    def trigger_scarcity_alert(self, part_name: str, machine_id: str):
        """
        Trigger a scarcity alert for a specific part.
        
        WHAT: Notifies management that a part is running low/out.
        HOW: Logs the alert (production would send email via SMTP).
        BIG PICTURE: Called when user clicks "Report Scarcity" in frontend.
        
        In production, this would:
        - Send email to procurement team
        - Create a purchase order in ERP
        - Log to maintenance history
        
        Args:
            part_name: Name of the scarce part.
            machine_id: Machine that needs the part.
            
        Returns:
            dict: Status message confirming the alert was sent.
        """
        # In a real app, this would send an email via SMTP
        # Example: smtplib.send_mail(to="management@factory.com", subject=f"Low Stock: {part_name}")
        print(f"ALERT: Scarcity reported for {part_name} (Machine: {machine_id}). Email sent to management@factory.com")
        return {"status": "success", "message": f"Alert sent to management for {part_name}."}


# Global singleton instance
# Created once when module is imported
inventory_service = InventoryService()

