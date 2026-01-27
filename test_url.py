import requests

urls = [
    "https://github.com",
    "http://paypal-login.verify.xyz",
    "https://free-gift-card.claim-now.info",
    "https://google.com",
    "http://secure-bank-update-alert.ru"
]

for url in urls:
    try:
        response = requests.post(
            "http://localhost:5000/predict",
            json={"url": url},
            timeout=5
        )
        print(url, "=>", response.json())
    except Exception as e:
        print(url, "=> ERROR:", e)
