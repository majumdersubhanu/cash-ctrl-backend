import argparse
import os
import subprocess
import sys
import time


def start_services():
    """Starts background services based on the OS."""
    print("Starting background services...")

    if os.name == "nt":  # Windows
        try:
            # Start Redis inside WSL
            subprocess.Popen(
                ["wsl", "redis-server"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            print("Redis server started inside WSL.")
        except Exception as e:
            print(f"Failed to start Redis via WSL: {e}")
    else:
        subprocess.Popen(["redis-server"])
        print("Redis server started.")


def start_django(env_name):
    """Starts the Django development server."""
    print(f"Starting Django with env: {env_name}")

    # Establish which env file to use
    env_file = ".env.dev" if env_name == "dev" else ".env"
    os.environ["DJANGO_ENV_FILE"] = env_file
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "app.settings")

    # Pass the env variable to the subprocess
    subprocess.call([sys.executable, "manage.py", "runserver"])


def start_celery():
    """Starts the Celery worker."""
    print("Starting Celery worker...")
    subprocess.Popen(
        [sys.executable, "-m", "celery", "-A", "app", "worker", "-l", "info"]
    )


def main():
    parser = argparse.ArgumentParser(description="CashCtrl Backend Entry Point")
    parser.add_argument(
        "--env",
        choices=["dev", "staging", "prod"],
        default="dev",
        help="Environment Selection",
    )
    parser.add_argument(
        "--start-services",
        action="store_true",
        help="Automatically start background services (Redis, Celery)",
    )

    args = parser.parse_args()

    if args.start_services:
        start_services()
        time.sleep(2)
        start_celery()

    start_django(args.env)


if __name__ == "__main__":
    main()
