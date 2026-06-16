import requests

TOKEN = "eyJraWQiOiJmNmE2OGNiMS1jNTY4LTQ0ZDMtYWFhZS1hYmI0NmJiMmE4ODAiLCJ0eXAiOiJKV1QiLCJhbGciOiJSUzM4NCJ9"
TRACKING_NUMBER = "1ZAX46436878291622"  # replace with your number

url = f"https://wwwcie.ups.com/api/track/v1/details/{TRACKING_NUMBER}"

headers = {
    "Authorization": f"Bearer {TOKEN}",
    "transId": "12345",
    "transactionSrc": "testing"
}

response = requests.get(url, headers=headers)

print(response.status_code)
print(response.json())
