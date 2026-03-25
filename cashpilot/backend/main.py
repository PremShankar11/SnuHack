from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from api.router import router as ingest_router
from dotenv import load_dotenv
import os

# Ensure environment is loaded right at startup
current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.dirname(current_dir)
dotenv_path = os.path.join(root_dir, '.env')
load_dotenv(dotenv_path)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Auto-seed fresh simulation data on every startup."""
    print("\n🚀 CashPilot starting up — seeding fresh simulation data...")
    try:
        from scripts.seed_data import seed_database
        from scripts.plaid_simulator import generate_simulator_data
        seed_database()
        generate_simulator_data()
        print("✅ Fresh simulation data ready!\n")
    except Exception as e:
        print(f"⚠️  Auto-seed failed (non-fatal): {e}\n")
    yield

app = FastAPI(
    title="CashPilot Backend API",
    description="AI-driven Financial Autopilot for SMBs - Perception Layer",
    version="1.0.0",
    lifespan=lifespan
)

# CORS config
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In production, restrict this
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Stream 1 & 2 Routers
from api.simulation_router import router as sim_router
from api.dashboard_router import router as dash_router
from api.quant_routes import router as quant_router
app.include_router(ingest_router, tags=["Ingestion"])
app.include_router(sim_router, tags=["Simulation Engine"])
app.include_router(dash_router, tags=["Dashboard & UI (Legacy)"])
app.include_router(quant_router, prefix="/quant", tags=["Quant Engine"])

@app.get("/")
def read_root():
    return {"message": "Welcome to the CashPilot Perception Layer API"}

if __name__ == "__main__":
    import uvicorn
    # Make sure to run the server from the `backend` directory
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)

