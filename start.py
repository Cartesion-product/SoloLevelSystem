"""Unified startup script for SoloLevelSystem backend.

This script launches both the FastAPI application and the Celery worker
simultaneously, ensuring both are running for full functionality.
"""

import subprocess
import sys
import time

def start_services():
    print("🚀 Starting SoloLevelSystem Backend Services...")

    # Start FastAPI (Uvicorn)
    print("▶️  Starting FastAPI (app.main)...")
    app_process = subprocess.Popen(
        [sys.executable, "-m", "app.main"],
        stdout=sys.stdout,
        stderr=sys.stderr,
    )

    # Give the app a moment to initialize its environment
    time.sleep(2)

    # Start Celery Worker
    # Note: do NOT pass -l/--loglevel here; our setup_logging signal handler
    # controls the log level via settings.LOG_LEVEL to avoid handler conflicts.
    print("▶️  Starting Celery Worker (app.tasks.celery_app)...")
    celery_process = subprocess.Popen(
        [sys.executable, "-m", "celery", "-A", "app.tasks.celery_app", "worker", "--pool=solo"],
        stdout=sys.stdout,
        stderr=sys.stderr,
    )

    print("\n✅ Both services started successfully.")
    print("   - API Logs:    logs/app/app.log")
    print("   - Celery Logs: logs/celery/celery.log")
    print("\nPress Ctrl+C to stop both services.\n")

    try:
        # Keep the main thread alive to watch the subprocesses
        while True:
            time.sleep(1)
            # If either process dies unexpectedly, we could choose to kill the other
            if app_process.poll() is not None:
                print("⚠️ FastAPI process exited.")
                break
            if celery_process.poll() is not None:
                print("⚠️ Celery process exited.")
                break
    except KeyboardInterrupt:
        print("\n🛑 Stopping services...")
    finally:
        celery_process.terminate()
        app_process.terminate()
        celery_process.wait()
        app_process.wait()
        print("✅ Services stopped cleanly.")

if __name__ == "__main__":
    start_services()
