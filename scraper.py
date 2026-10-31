import requests
from bs4 import BeautifulSoup
from feedgenerator import Rss201rev2Feed
import datetime
import re

url = "https://careercircle.com"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9"
}

response = requests.get(url, headers=headers)
soup = BeautifulSoup(response.text, 'html.parser')

feed = Rss201rev2Feed(
    title="CareerCircle - Remote Change Manager Jobs",
    link=url,
    description="Automated feed tracking the latest Remote Change Manager roles on CareerCircle",
    language="en"
)

job_titles = soup.find_all(text=re.compile(r'(Change Management|Change Manager|Project Manager)', re.IGNORECASE))
seen_titles = set()
count = 0

for element in job_titles:
    if count >= 15:
        break
    parent = element.parent
    if parent.name in ['a', 'h2', 'h3', 'h4', 'span']:
        title_text = element.strip()
        if title_text in seen_titles or len(title_text) > 100:
            continue
        seen_titles.add(title_text)
        feed.add_item(
            title=title_text,
            link=url,
            description=f"New Remote Position matching criteria found: {title_text}",
            pubdate=datetime.datetime.now()
        )
        count += 1

with open("feed.xml", "w", encoding="utf-8") as f:
    feed.write(f, 'utf-8')
print("Successfully generated feed.xml file!")
