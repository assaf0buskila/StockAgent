"""
Startup script for AgentStock application.
Run this file to start the server.
"""

import sys
from pathlib import Path

# Add the backend directory to Python path
backend_dir = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_dir))

import uvicorn

if __name__ == "__main__":
    print("🚀 Starting AgentStock Server...")
    print("=" * 50)
    
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )