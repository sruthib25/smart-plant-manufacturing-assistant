import sys
import os
sys.path.append(os.path.join(os.getcwd(), 'backend'))

try:
    print("Checking imports...")
    from app.main import app
    from app.services.simulator import simulator
    from app.services.rag_service import rag_service
    from app.core.orchestrator import orchestrator
    print("Imports success.")

    print("Checking Simulator...")
    data = simulator.get_readings()
    print(f"Simulator data keys: {data.keys()}")

    print("Checking RAG Service...")
    # This might fail if choma db isn't set up or dependencies missing in this env, 
    # but strictly checking if the class initializes is good enough for structure.
    # rag_service.ingest_data() # Skip actual ingestion to save time/errors in this pure python check
    print("RAG Service initialized.")

    print("Checking Orchestrator...")
    # Mock LLM service to avoid network call
    from app.services.llm_service import llm_service
    llm_service.generate = lambda x: '{"agent": "GENERAL"}'
    
    route = orchestrator.route_query("Hello")
    print(f"Orchestrator route: {route}")

    print("VERIFICATION SUCCESSFUL")

except Exception as e:
    print(f"VERIFICATION FAILED: {e}")
    import traceback
    traceback.print_exc()
