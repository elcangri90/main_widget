import base64
import requests

# -----------------------------
# 1. GET OAUTH TOKEN
# -----------------------------

CLIENT_ID = "1lasVvgYvQhnF8TdbHfIKJRdfXlKBlj2TIzEu2kDcSQiP7yw"
CLIENT_SECRET = "snqnAPpvGgeYbegkRVBLw5Z3c49BRxYGIjrxM79sVNAY0DIA4nCAWJS5lBF9WEiK"

def get_token():
    auth = f"{CLIENT_ID}:{CLIENT_SECRET}"
    auth_base64 = base64.b64encode(auth.encode()).decode()

    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Authorization": f"Basic {auth_base64}"
    }

    data = {
        "grant_type": "client_credentials"
    }

    response = requests.post(
        "https://wwwcie.ups.com/security/v1/oauth/token",
        headers=headers,
        data=data
    )

    if response.status_code != 200:
        print("Error getting token:", response.text)
        return None

    return response.json()["access_token"]


# -----------------------------
# 2. TRACKING REQUEST
# -----------------------------

def track_package(tracking_number, token):
    url = f"https://wwwcie.ups.com/api/track/v1/details/{tracking_number}"

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}",
        "transId": "12345",
        "transactionSrc": "testing"
    }

    body = {
        "locale": "en_US"
    }

    response = requests.post(url, headers=headers, json=body)

    print("Status:", response.status_code)
    try:
        print(response.json())
    except:
        print(response.text)


# -----------------------------
# 3. MAIN PROGRAM
# -----------------------------

if __name__ == "__main__":
    tracking_number = input("Enter UPS tracking number: ")

    token = get_token()
    if token:
        track_package(tracking_number, token)
