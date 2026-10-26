import requests
import os
import json
from dotenv import load_dotenv
load_dotenv()
ACCESS_TOKEN = os.environ["META_ACCESS_TOKEN"]
AD_ACCOUNT_ID = "act_1636583850695699"  # must include act_ prefix

BASE_URL = f"https://graph.facebook.com/v21.0/{AD_ACCOUNT_ID}/ads"

params = {
    "access_token": ACCESS_TOKEN,
    "fields": (
        "id,name,status,"
        "adset{id,name,daily_budget,lifetime_budget},"
        "campaign{id,name},"
        "insights.date_preset(last_30d){spend,impressions,clicks,ctr}"
    ),
    "limit": 100,
}

def fetch_ads_data():
    ads_data = []
    url = BASE_URL
    request_params = dict(params)  # local copy

    while url:
        response = requests.get(url, params=request_params, verify=False)
        data = response.json()
        print(json.dumps(data, indent=2))
        if "error" in data:
            print("Meta API error:", data["error"])
            break

        for ad in data.get("data", []):
            insights = ad.get("insights", {}).get("data", [{}])
            insight = insights[0] if insights else {}

            spend = insight.get("spend", "0")
            impressions = insight.get("impressions", "0")
            clicks = insight.get("clicks", "0")
            ctr = insight.get("ctr")
            ctr_str = f"{float(ctr):.2f}%" if ctr is not None else "0%"

            text_chunk = (
                f"Ad ID: {ad.get('id')}. Name: {ad.get('name')}. "
                f"Status: {ad.get('status')}. Campaign: {ad.get('campaign', {}).get('name')}. "
                f"Spend: ${spend}. Impressions: {impressions}. Clicks: {clicks}. CTR: {ctr_str}."
            )
            ads_data.append(text_chunk)

        paging = data.get("paging", {})
        url = paging.get("next")
        request_params = {}  # subsequent "next" URLs already have all params encoded

    print(f"Fetched {len(ads_data)} ad summaries.")
    return ads_data

if __name__ == "__main__":
    data = fetch_ads_data()
    if data:
        with open("meta_ads_data.txt", "w", encoding="utf-8") as f:
            f.write("\n".join(data))
        print("Saved to meta_ads_data.txt")