import requests

NEWS_API_KEY = '70c84f029e58455583cd8ffa08843184'  # Your API key

def fetch_islamic_news():
    url = (
        "https://newsapi.org/v2/everything?"
        "q=(Islamic OR Muslim OR Quran OR Hajj OR Umrah OR Mosque OR Sharia OR Halal OR Hijab "
        "OR Islamic culture OR Islamic society OR Eid OR Zakat OR Hadith OR Islamic community)"
        " AND NOT (terrorist OR violence OR crime OR radical OR extremist OR ISIS OR ISIL OR Taliban OR conflict)"
        "&language=en"
        "&sortBy=publishedAt"
        "&pageSize=20"
        f"&apiKey={NEWS_API_KEY}"
    )

    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        return data.get('articles', [])
    except Exception as e:
        print("Error fetching news:", e)
        return []
