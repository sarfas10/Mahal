import requests

FIREBASE_API_KEY = "AIzaSyCoyZlJgdEL2ZScKvOjYL3YTCc27Ho68Qc"
FIREBASE_AUTH_URL = "https://identitytoolkit.googleapis.com/v1/accounts"
FIREBASE_PROJECT_ID = "mahal-f71d2" 
def firebase_login(email, password):
    url = f"{FIREBASE_AUTH_URL}:signInWithPassword?key={FIREBASE_API_KEY}"
    payload = {
        "email": email,
        "password": password,
        "returnSecureToken": True
    }
    response = requests.post(url, json=payload)
    data = response.json()
    if response.status_code == 200:
        return data  # contains idToken, localId, etc.
    else:
        raise Exception(data.get("error", {}).get("message", "Login failed"))

def firebase_register(email, password, name):
    # Step 1: Register the user
    url = f"{FIREBASE_AUTH_URL}:signUp?key={FIREBASE_API_KEY}"
    payload = {
        "email": email,
        "password": password,
        "returnSecureToken": True
    }
    response = requests.post(url, json=payload)
    data = response.json()

    if response.status_code != 200:
        raise Exception(data.get("error", {}).get("message", "Registration failed"))

    id_token = data["idToken"]
    local_id = data["localId"]

    # Step 2: Create Firestore document for the user
    firestore_url = f"https://firestore.googleapis.com/v1/projects/{FIREBASE_PROJECT_ID}/databases/(default)/documents/users/{local_id}"
    firestore_payload = {
        "fields": {
            "name": {"stringValue": name},
            "email": {"stringValue": email},
            "role": {"stringValue": "user"}
        }
    }
    headers = {
        "Authorization": f"Bearer {id_token}",
        "Content-Type": "application/json"
    }
    firestore_response = requests.patch(firestore_url, headers=headers, json=firestore_payload)

    if firestore_response.status_code not in [200, 201]:
        raise Exception("User registered, but failed to create Firestore user document.")

    return data  # Optional, return if needed
