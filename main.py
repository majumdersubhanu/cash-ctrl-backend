import argparse
import os
import sys
import subprocess
import time

def start_services():
    """Starts background services based on the OS."""
    print("Starting background services...")
    
    # Check if Redis is running (simple check)
    if os.name == 'nt':  # Windows
        try:
            # Attempt to start redis if it's in the path
            subprocess.Popen(['redis-server'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            print("Redis server started (Windows).")
        except FileNotFoundError:
            print("Warning: redis-server not found. Please ensure it's installed and in PATH.")
    else:
        print("Service orchestration logic for non-Windows platforms would go here.")

def start_django(env_name):
    """Starts the Django development server."""
    print(f"Starting Django with env: {env_name}")
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'app.settings')
    # In a real app, env_name would choose different settings files or .env files
    # For now, we follow the user's wish for flag selection
    subprocess.call(['py', 'manage.py', 'runserver'])

def start_celery():
    """Starts the Celery worker."""
    print("Starting Celery worker...")
    subprocess.Popen(['py', '-m', 'celery', '-A', 'app', 'worker', '-l', 'info'])

def main():
    parser = argparse.ArgumentParser(description="CashCtrl Backend Entry Point")
    parser.add_argument('--env', choices=['dev', 'staging', 'prod'], default='dev', help="Environment Selection")
    parser.add_argument('--start-services', action='store_true', help="Automatically start background services (Redis, Celery)")
    
    args = parser.parse_args()

    if args.start_services:
        start_services()
        # Wait a bit for redis to be ready
        time.sleep(2)
        start_celery()

    start_django(args.env)

if __name__ == "__main__":
    main()
