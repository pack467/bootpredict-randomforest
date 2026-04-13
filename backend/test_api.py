"""Quick API test script for verification."""
import urllib.request
import json

BASE = "http://localhost:8000"

def api(method, path, token=None, data=None):
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    body = json.dumps(data).encode() if data else None
    req = urllib.request.Request(f"{BASE}{path}", data=body, headers=headers, method=method)
    resp = urllib.request.urlopen(req)
    return json.loads(resp.read())

# 1. Login
print("=" * 50)
print("TEST 1: Login")
r = api("POST", "/api/auth/login", data={"username": "admin", "password": "admin123"})
token = r["access_token"]
print(f"  OK - User: {r['user']['username']} ({r['user']['role']})")

# 2. Register new user
print("\nTEST 2: Register")
try:
    r = api("POST", "/api/auth/register", data={"username": "testuser", "password": "test1234"})
    print(f"  OK - Created: {r['user']['username']}")
    test_token = r["access_token"]
except Exception as e:
    print(f"  SKIP - User exists (expected)")
    r = api("POST", "/api/auth/login", data={"username": "testuser", "password": "test1234"})
    test_token = r["access_token"]

# 3. Get /api/auth/me
print("\nTEST 3: Auth Me")
r = api("GET", "/api/auth/me", token=token)
print(f"  OK - {r}")

# 4. Prediction
print("\nTEST 4: Prediction (speed/nike/striker)")
r = api("POST", "/api/predict", token=test_token, data={"peminatan": "speed", "brand": "nike", "posisi": "striker"})
print(f"  OK - Class: {r['predicted_class']}")
print(f"  Probabilities: {r['probabilities']}")
print(f"  Feature Importance: {r['feature_importance']}")
print(f"  Products: {len(r.get('recommended_products', []))}")
print(f"  Explanation: {r['explanation'][:100]}...")

# 5. Another prediction
print("\nTEST 5: Prediction (control/adidas/midfielder)")
r = api("POST", "/api/predict", token=test_token, data={"peminatan": "control", "brand": "adidas", "posisi": "midfielder"})
print(f"  OK - Class: {r['predicted_class']}")
print(f"  Probabilities: {r['probabilities']}")

# 6. History
print("\nTEST 6: History")
r = api("GET", "/api/history", token=test_token)
print(f"  OK - Count: {len(r)}")
for i, h in enumerate(r[:3]):
    print(f"  #{i+1}: {h['peminatan']}/{h['brand']}/{h['posisi']} -> {h['predicted_class']}")

# 7. Stats
print("\nTEST 7: Stats")
r = api("GET", "/api/history/stats", token=test_token)
print(f"  OK - {r}")

# 8. Admin Dashboard
print("\nTEST 8: Admin Dashboard")
r = api("GET", "/api/admin/dashboard", token=token)
print(f"  OK - Users: {r['total_users']}, Predictions: {r['total_predictions']}, Dataset: {r['total_dataset_records']}")
if r["latest_training"]:
    t = r["latest_training"]
    print(f"  Training: acc={t['accuracy']}, cv_mean={t.get('cv_mean_accuracy')}")

# 9. Training Logs
print("\nTEST 9: Training Logs")
r = api("GET", "/api/admin/training-logs", token=token)
print(f"  OK - Logs: {len(r)}")

# 10. Health Check
print("\nTEST 10: Health")
r = api("GET", "/api/health")
print(f"  OK - {r}")

print("\n" + "=" * 50)
print("ALL TESTS PASSED ✅")
print("=" * 50)
