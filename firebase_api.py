import requests

FIREBASE_API_KEY = "AIzaSyCoyZlJgdEL2ZScKvOjYL3YTCc27Ho68Qc"
FIREBASE_AUTH_URL = "https://identitytoolkit.googleapis.com/v1/accounts"

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

def firebase_register(email, password):
    url = f"{FIREBASE_AUTH_URL}:signUp?key={FIREBASE_API_KEY}"
    payload = {
        "email": email,
        "password": password,
        "returnSecureToken": True
    }
    response = requests.post(url, json=payload)
    data = response.json()
    if response.status_code == 200:
        return data
    else:
        raise Exception(data.get("error", {}).get("message", "Registration failed"))

def firebase_send_reset(email):
    url = f"{FIREBASE_AUTH_URL}:sendOobCode?key={FIREBASE_API_KEY}"
    payload = {
        "requestType": "PASSWORD_RESET",
        "email": email
    }
    response = requests.post(url, json=payload)
    data = response.json()
    if response.status_code == 200:
        return True
    else:
        raise Exception(data.get("error", {}).get("message", "Reset email failed"))
