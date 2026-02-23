from app.main import app
from collections import Counter

route_identifiers = []
for route in app.routes:
    methods = sorted(list(getattr(route, 'methods', [])))
    for method in methods:
        route_identifiers.append((route.path, method))

counts = Counter(route_identifiers)

print("ACTUAL DUPLICATE (PATH, METHOD) COMBINATIONS:")
found_duplicates = False
for (path, method), count in counts.items():
    if count > 1:
        print(f"{method} {path}: {count} times")
        found_duplicates = True

if not found_duplicates:
    print("No identical (path, method) combinations found.")

print("\nLIST OF ALL ENDPOINTS:")
for route in app.routes:
    methods = sorted(list(getattr(route, 'methods', [])))
    endpoint = getattr(route, 'endpoint', None)
    module = getattr(endpoint, '__module__', 'N/A')
    name = getattr(route, 'name', 'N/A')
    print(f"{methods} {route.path} | {module} | {name}")
