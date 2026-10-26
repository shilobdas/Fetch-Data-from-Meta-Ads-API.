import os
import requests
from dotenv import load_dotenv

load_dotenv()  # reads .env and loads it into environment variables

META_ACCESS_TOKEN = os.environ["META_ACCESS_TOKEN"]
AD_ACCOUNT_ID = "act_1636583850695699"

url = f"https://graph.facebook.com/v21.0/{AD_ACCOUNT_ID}"
params = {
    "access_token": META_ACCESS_TOKEN,
    "fields": "id,name,account_status,currency,timezone_name,business_name,age,created_time,disable_reason,spend_cap,amount_spent,balance"
}

response = requests.get(url, params=params, verify=False)
print(response.json())