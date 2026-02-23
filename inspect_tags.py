from app.main import app

print("ENDPOINT TAGS VERIFICATION:")
for route in app.routes:
    if hasattr(route, "endpoint"):
        tags = getattr(route, "tags", [])
        print(f"{route.path} | {tags}")
