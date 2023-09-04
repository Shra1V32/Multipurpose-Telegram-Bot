import requests
from constants import GDRIVE_CLIENT_ID, GDRIVE_CLIENT_SECRET, GDRIVE_REFRESH_TOKEN


def genToken():
    # Make a request to the token endpoint to refresh the access token
    response = requests.post(
        "https://oauth2.googleapis.com/token",
        data={
            "client_id": GDRIVE_CLIENT_ID,
            "client_secret": GDRIVE_CLIENT_SECRET,
            "refresh_token": GDRIVE_REFRESH_TOKEN,
            "grant_type": "refresh_token",
        },
    )

    # If the request is successful, the response will contain a new access token
    response.raise_for_status()
    access_token = response.json()["access_token"]

    with open("gdrivetoken", "w") as outfile:
        outfile.write(access_token)
        outfile.close()


if __name__ == "__main__":
    genToken()
