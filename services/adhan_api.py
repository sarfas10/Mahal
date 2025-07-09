# services/adhan_api.py

import requests
from datetime import datetime

def fetch_adhan_times(city="Calicut", country="India", method=2):
    """
    Fetch today's Adhan times using Aladhan API.
    Args:
        city (str): City name
        country (str): Country name
        method (int): Calculation method (default 2 = University of Islamic Sciences, Karachi)
    Returns:
        dict: Dictionary of prayer names and their times, or empty dict on failure
    """
    today = datetime.now().strftime("%d-%m-%Y")
    url = f"http://api.aladhan.com/v1/timingsByCity/{today}"
    
    params = {
        "city": city,
        "country": country,
        "method": method
    }

    try:
        response = requests.get(url, params=params, timeout=5)
        data = response.json()
        if response.status_code == 200 and data["code"] == 200:
            timings = data["data"]["timings"]
            return {
                "Fajr": timings["Fajr"],
                "Dhuhr": timings["Dhuhr"],
                "Asr": timings["Asr"],
                "Maghrib": timings["Maghrib"],
                "Isha": timings["Isha"]
            }
        else:
            print("Failed to fetch Adhan times:", data)
    except Exception as e:
        print("Error fetching Adhan times:", e)

    return {}
