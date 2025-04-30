from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time
import requests

# === CONFIG ===
SEARCH_KEYWORD = "airpods max"
MAX_RESULTS = 5
MAX_LISTINGS_TO_SCAN = 40

TELEGRAM_BOT_TOKEN = "8067218605:AAEZ-dCPSIHx0T3BNzVjDBZ0dMehOkG6TlA"
TELEGRAM_CHAT_ID = "5768567714"
LOG_FILE = "top_watchers_log.txt"

# === Browser Setup ===
options = Options()
options.add_argument("--headless")
options.add_argument("--disable-gpu")
driver = webdriver.Chrome(options=options)

# === Helpers ===
def send_telegram(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    data = {"chat_id": TELEGRAM_CHAT_ID, "text": message}
    try:
        requests.post(url, data=data)
    except Exception as e:
        print(f"[ERROR] Telegram error: {e}")

def log_listing(title, watchers, price, link):
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"{title} - {watchers} watchers - ${price}\n{link}\n\n")

def extract_watchers(url):
    try:
        driver.get(url)
        time.sleep(2)
        text_blocks = driver.find_elements(By.CSS_SELECTOR, "span")
        for block in text_blocks:
            txt = block.text.lower()
            if "watching" in txt or "watchers" in txt:
                num = ''.join(filter(str.isdigit, txt))
                return int(num) if num else 0
    except:
        return 0
    return 0

def scan_most_watched(keyword):
    print(f"\n🔍 Scanning eBay for most-watched: {keyword}")
    url = f"https://www.ebay.com/sch/i.html?_nkw={keyword.replace(' ', '+')}&_sop=12&LH_BIN=1"
    driver.get(url)
    time.sleep(3)

    listings = driver.find_elements(By.CSS_SELECTOR, ".s-item__link")[:MAX_LISTINGS_TO_SCAN]
    data = []

    for link in listings:
        try:
            href = link.get_attribute("href")
            title = link.text.split("\n")[0]
            price_el = link.find_element(By.XPATH, '../../..//span[@class="s-item__price"]')
            price_text = price_el.text.replace("$", "").replace(",", "").split()[0]
            price = float(price_text)

            watchers = extract_watchers(href)
            print(f"Found: {title} | ${price} | 👁️ {watchers} watchers")
            data.append((title, watchers, price, href))
        except:
            continue

    top_items = sorted(data, key=lambda x: x[1], reverse=True)[:MAX_RESULTS]

    for item in top_items:
        title, watchers, price, link = item
        msg = f"👀 {watchers} watchers\n📦 {title}\n💰 ${price}\n🔗 {link}"
        send_telegram(msg)
        log_listing(title, watchers, price, link)

    print(f"\n✅ Sent top {len(top_items)} most-watched listings to Telegram.")

# === Run Bot ===
scan_most_watched(SEARCH_KEYWORD)
driver.quit()
