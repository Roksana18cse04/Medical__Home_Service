import asyncio
import subprocess
import threading
import time
import os
import sys

async def run_fastapi():
    """Run FastAPI backend server asynchronously"""
    print("🚀 Starting FastAPI Backend Server...")
    try:
        process = await asyncio.create_subprocess_exec(
            sys.executable, "-m", "uvicorn", 
            "app.main:app", 
            "--reload", 
            "--host", "0.0.0.0", 
            "--port", "8000",
            cwd=os.getcwd()
        )
        await process.wait()
    except Exception as e:
        print(f"❌ FastAPI Error: {e}")

async def run_streamlit():
    """Run Streamlit frontend asynchronously"""
    print("🎨 Starting Streamlit Frontend...")
    await asyncio.sleep(3)  # Wait for FastAPI to start
    try:
        process = await asyncio.create_subprocess_exec(
            sys.executable, "-m", "streamlit", 
            "run", "streamlit_app.py", 
            "--server.port", "8501",
            "--server.headless", "true",
            cwd=os.getcwd()
        )
        await process.wait()
    except Exception as e:
        print(f"❌ Streamlit Error: {e}")

async def main():
    print("🏥 MediUrgency Healthcare Platform")
    print("=" * 50)
    print("Starting Backend and Frontend servers...")
    print("Backend API: http://localhost:8000")
    print("Frontend UI: http://localhost:8501")
    print("=" * 50)
    
    # Run both servers concurrently
    await asyncio.gather(
        run_fastapi(),
        run_streamlit()
    )

if __name__ == "__main__":
    asyncio.run(main())