import asyncio
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
from feedgenerator import Rss201rev2Feed
import datetime

async def main():
    url = "https://careercircle.com"
    
    async with async_playwright() as p:
        # Launch a headless browser window
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        # Go to the site and wait for the job list elements to load into view
        print("Opening CareerCircle...")
        await page.goto(url, wait_until="networkidle")
        await page.wait_for_timeout(5000) # Give JavaScript an extra 5 seconds to load cards
        
        # Grab the fully rendered HTML page source
        html = await page.content()
        await browser.close()

    soup = BeautifulSoup(html, 'html.parser')
    
    # Initialize the RSS Feed
    feed = Rss201rev2Feed(
        title="CareerCircle - Remote Change Manager Jobs",
        link=url,
        description="Automated feed tracking the latest Remote Change Manager roles on CareerCircle",
        language="en"
    )

    # Hunt for the specific job card containers or titles in the loaded DOM
    # Looking for headings and bold texts that likely house titles
    job_elements = soup.find_all(['h2', 'h3', 'h4', 'div', 'span'])
    
    seen_titles = set()
    count = 0
    
    # Common job related keywords to filter from text scraps
    keywords = ["change management", "change manager", "project manager", "enablement process"]

    for el in job_elements:
        text = el.get_text().strip()
        # Ensure it matches our criteria, isn't a duplicate, and looks like a title length
        if any(kw in text.lower() for kw in keywords) and len(text) < 80:
            if text in seen_titles:
                continue
            seen_titles.add(text)
            
            feed.add_item(
                title=text,
                link=url,
                description=f"Remote role listed on CareerCircle: {text}",
                pubdate=datetime.datetime.now()
            )
            count += 1
            if count >= 20:
                break

    # Save out the finished file
    with open("feed.xml", "w", encoding="utf-8") as f:
        feed.write(f, 'utf-8')
    print(f"Successfully generated feed.xml with {count} jobs!")

if __name__ == "__main__":
    asyncio.run(main())
