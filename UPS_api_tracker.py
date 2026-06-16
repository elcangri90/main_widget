import base64
import requests

CLIENT_ID = "1lasVvgYvQhnF8TdbHfIKJRdfXlKBlj2TIzEu2kDcSQiP7yw"
CLIENT_SECRET = "snqnAPpvGgeYbegkRVBLw5Z3c49BRxYGIjrxM79sVNAY0DIA4nCAWJS5lBF9WEiK"

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

print(response.status_code)
print(response.text)
