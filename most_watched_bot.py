import requests
from bs4 import BeautifulSoup

# === CONFIG ===
KEYWORDS = ["airpods max"]
MAX_RESULTS = 5
TELEGRAM_BOT_TOKEN = "8067218605:AAEZ-dCPSIHx0T3BNzVjDBZ0dMehOkG6TlA"
TELEGRAM_CHAT_ID = "5768567714"

def send_telegram(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    data = {"chat_id": TELEGRAM_CHAT_ID, "text": message}
    requests.post(url, data=data)

def scrape_ebay(keyword):
    url = f"https://www.ebay.com/sch/i.html?_nkw={keyword.replace(' ', '+')}&_sop=12&LH_BIN=1"
    headers = {"User-Agent": "Mozilla/5.0"}
    res = requests.get(url, headers=headers)
    soup = BeautifulSoup(res.text, "html.parser")
    listings = soup.select(".s-item")[:20]

    results = []
    for item in listings:
        title = item.select_one(".s-item__title")
        watchers = item.select_one(".s-item__hotness")
        price = item.select_one(".s-item__price")
        link = item.select_one(".s-item__link")

        if title and watchers and price and link:
            num_watchers = ''.join(filter(str.isdigit, watchers.text))
            results.append((int(num_watchers), title.text, price.text, link["href"]))

    for count, title, price, url in sorted(results, reverse=True)[:MAX_RESULTS]:
        msg = f"👀 {count} watchers\n📦 {title}\n💰 {price}\n🔗 {url}"
        send_telegram(msg)

for kw in KEYWORDS:
    scrape_ebay(kw)
