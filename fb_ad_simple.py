import requests
import os
from dotenv import load_dotenv

load_dotenv()
ACCESS_TOKEN = os.environ["META_ACCESS_TOKEN"]
AD_ACCOUNT_ID = "act_1636583850695699"

url = f"https://graph.facebook.com/v21.0/{AD_ACCOUNT_ID}/ads"
params = {
    "access_token": ACCESS_TOKEN,
    "fields": "id,name,status"
}

response = requests.get(url, params=params, verify=False)
print(response.json())