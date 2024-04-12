import requests


def get_token():
    url = "https://test.api.amadeus.com/v1/security/oauth2/token"

    payload = {
        "grant_type": "client_credentials",
        "client_id": "hIZTAlgRLX9HjY7Dv4eXya11p1Kiw9kN",
        "client_secret": "Mn6s49VqIGGX2KlM"
    }

    response = requests.post(url, data=payload)
    token = None
    # Check if the request was successful
    if response.status_code == 200:
        data = response.json()
        token = data.get('access_token')
        print(token)
    else:
        print(f"Request failed with status code {response.status_code}")

    return token
