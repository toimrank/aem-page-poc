import requests
from bs4 import BeautifulSoup, SoupStrainer
from urllib.parse import urlparse
from datetime import datetime, timedelta
import random
from dateutil.relativedelta import relativedelta
import json
from utils.utils import random_email, random_name, random_time, get_locale_from_url

page_list = [
    "https://www.americanexpress.com/en-us/newsroom/articles/shop-small/american-express--founder-of-small-business-saturday---expands-s.html",
        "https://www.americanexpress.com/en-us/newsroom/articles/shop-small/2025-american-express-shop-small-impact-study-results.html",
        "https://www.americanexpress.com/en-us/newsroom/articles/shop-small/how-a-brooklyn-general-goods-store-became-a-beloved-community-st.html",
        "https://www.americanexpress.com/en-us/newsroom/articles/colleagues-and-culture/130-years-in-france--inside-amex-s-iconic-paris-address.html",
        "https://www.americanexpress.com/en-us/newsroom/articles/corporate-sustainability/top-takeaways-from-paris-hilton--leslie-odom--jr--and-taj-gibson.html",
        "https://www.americanexpress.com/en-us/newsroom/articles/entertainment-and-experiences/story-of-my-song--gracie-abrams-shares-what-inspired-her-viral-h.html",
        "https://www.americanexpress.com/en-us/newsroom/articles/colleagues-and-culture/american-express-named-no--1-on-great-place-to-work-s-2025-list-.html",
        "https://www.americanexpress.com/en-us/newsroom/articles/corporate-sustainability/chairman-and-ceo-steve-squeri-shares-leadership-lessons-at-the-a.html",
        "https://www.americanexpress.com/en-us/newsroom/articles/entertainment-and-experiences/amex-access--olivia-rodrigo--fashion-and-fine-dining-from-brookl.html",
        "https://www.americanexpress.com/en-us/newsroom/articles/colleagues-and-culture/american-express-named-one-of-the-best-workplaces-for-women-in-t.html",
        "https://www.americanexpress.com/en-us/newsroom/articles/company-statements/american-express-supports-relief-and-recovery-efforts-for-hurric.html"
]


def page_create_date(publish_date_str, date_format="%m-%d-%Y"):
    """
    Given a publish date, generate:
    - Create date: 1 month before
    - Modified date: 5 days before
    Both dates include random time and ISO-8601 format.
    """
    # Parse publish date
    publish_date = datetime.strptime(publish_date_str, date_format)

    # Generate create date: 1 month back
    create_date = publish_date - relativedelta(months=1)
    ch, cm, cs = random_time()
    create_date = create_date.replace(hour=ch, minute=cm, second=cs)

    # Generate modified date: 5 days back
    modified_date = publish_date - timedelta(days=5)
    mh, mm, ms = random_time()
    modified_date = modified_date.replace(hour=mh, minute=mm, second=ms)

    # Format as ISO-8601
    return {
        "create_date": create_date.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "modified_date": modified_date.strftime("%Y-%m-%dT%H:%M:%SZ")
    }

def date_to_iso_with_random_time(date_str, date_format="%m-%d-%Y"):
    """
    Convert a date string to ISO-8601 with random time.
    Example: "12-09-2025" -> "2025-12-09T14:37:22Z"
    """
    # Parse the date
    dt = datetime.strptime(date_str, date_format)

    # Generate random hour, minute, second
    hour = random.randint(0, 23)
    minute = random.randint(0, 59)
    second = random.randint(0, 59)

    # Replace time in datetime
    dt = dt.replace(hour=hour, minute=minute, second=second)

    # Format as ISO-8601
    return dt.strftime("%Y-%m-%dT%H:%M:%SZ")

# Example usage
date_str = "12-09-2025"
iso_date = date_to_iso_with_random_time(date_str)
print(iso_date)

# Function to return 3 random keywords
def get_random_keywords(n=3):
    amex_keywords = [
        "credit card", "rewards", "points", "cashback", "membership", "platinum", 
        "gold", "travel", "insurance", "offers", "benefits", "loyalty", 
        "exclusive", "business", "corporate", "online banking", "mobile app", 
        "charge card", "finance", "payment", "secure", "customer service", 
        "account", "promotion", "upgrade", "welcome bonus", "travel perks", 
        "premium", "investment", "support"
    ]
    return random.sample(amex_keywords, n)

def get_date_format(iso_time):
    dt = datetime.fromisoformat(iso_time.replace("Z", "+00:00"))
    return dt.strftime("%Y-%m-%d %H:%M:%S%z")

def extract_page_data(url):
    # Fetch live page
    r = requests.get(url)
    r.raise_for_status()

    # Parse only the <head> part for faster performance
    head_only = SoupStrainer("head")
    soup = BeautifulSoup(r.text, "lxml", parse_only=head_only)

    # ---- Modern CSS selector style ----

    # Title
    title = soup.select_one("title")
    title = title.get_text(strip=True) if title else None

    # Description
    description = soup.select_one("meta[name=description]")
    description = description.get("content") if description else None

    # Canonical URL
    canonical = soup.select_one("link[rel=canonical]")
    canonical = canonical.get("href") if canonical else None

    # Publish date
    publish_date = soup.select_one("meta[name=publishDate]")
    publish_date = publish_date.get("content") if publish_date else None

    # Page name from AEM meta
    aem_meta = soup.select_one("meta[name=AEM]")
    
    path = urlparse(url).path  # /american-express--founder-of-small-business-saturday---expands-s
    page_name = path.strip("/").split("/")[-1]  # remove / and take the last part
    
    custom_date=page_create_date(publish_date)

    return {
        "page_name": page_name,
        "page_title": title,
        "description": description,
        "page_url": url,
        "tags" : get_random_keywords(3),
        "publish_date": get_date_format(date_to_iso_with_random_time(publish_date)),
        "create_date" : get_date_format(custom_date["create_date"]),
        "modified_date" : get_date_format(custom_date["modified_date"]),
        "created_by" : random_name(),
        "modified_by" : random_name(),
        "publish_by" : random_name(),
        "locale" : get_locale_from_url(canonical),
        "page_status" : "Activate",
        "page_scheduled_on_time" : "",
        "page_scheduled_off_time" : "",
        "businessUnit" : "",
        "content_owner_email" : random_email(),
        "seo": {
            "canonical_url": canonical,
            "robots": "index, follow",
            "seo_keywords" : get_random_keywords(3)
        }
    }

# -----------------------------
# 🔥 Example Usage
# -----------------------------

page_json_list = []
for url in page_list:
    data = extract_page_data(url)
    page_json_list.append(data)

print(">>>>>>>>>>>>>>>>>>>>")
print(page_json_list)

filename = "data.json"

# Write JSON data to file
with open(filename, "w") as file:
    json.dump(page_json_list, file, indent=4)

print(f"JSON data has been written to {filename}")