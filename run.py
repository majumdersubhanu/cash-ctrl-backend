import uvicorn
import argparse
import os

def main():
    parser = argparse.ArgumentParser(description="Run the CashCtrl API server.")
    parser.add_argument("--dev", action="store_true", help="Run in development mode with reload.")
    parser.add_argument("--prod", action="store_true", help="Run in production mode.")
    parser.add_argument("--port", type=int, default=8000, help="Port to run the server on.")
    parser.add_argument("--host", type=str, default="127.0.0.1", help="Host to bind the server to.")
    
    args = parser.parse_args()
    
    # In a real app, you might set environment variables here
    # Logic: Default to 'dev'. If --prod is passed, use 'prod'.
    os.environ["ENVIRONMENT"] = "prod" if args.prod else "dev"
    reload = args.dev or (not args.prod) # Reload in dev modes
        
    uvicorn.run(
        "app.main:app",
        host=args.host,
        port=args.port,
        reload=reload,
        log_level="info"
    )

if __name__ == "__main__":
    main()
