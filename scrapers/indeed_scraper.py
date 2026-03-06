from playwright.sync_api import sync_playwright
import requests
import time

API_URL = "http://127.0.0.1:8001/jobs"

def send_to_backend(job):
    resp = requests.post(API_URL, json=job)
    print(resp.status_code, resp.json())

def scrape_indeed():
    print("Scraper started")

    with sync_playwright() as p:
        # Run in visible mode so we can debug if needed
        browser = p.chromium.launch(headless=False)

        # Use a realistic browser user agent
        page = browser.new_page(
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/122.0.0.0 Safari/537.36"
            )
        )

        # Use a broad but valid search keyword
        url = "https://www.indeed.com/jobs?q=data&l=United+States"
        page.goto(url)

        print("Page loaded:", page.title())

        # Allow dynamic content to load
        time.sleep(5)

        # Indeed uses multiple layouts; try all
        selectors = [
            "div.job_seen_beacon",
            "td.resultContent",
            "div.slider_container",
        ]

        cards = []
        for sel in selectors:
            found = page.query_selector_all(sel)
            if found:
                cards = found
                print(f"Using selector: {sel} — found {len(cards)} jobs")
                break

        if not cards:
            print("No job cards found. Indeed may be blocking the scraper.")
            print("Page HTML preview:")
            print(page.content()[:1000])
            browser.close()
            return

        # Extract job data and send to backend
        for card in cards:
            title_el = card.query_selector("h2 span")
            company_el = card.query_selector("span.companyName")
            location_el = card.query_selector("div.companyLocation")

            if not (title_el and company_el and location_el):
                continue

            job = {
                "title": title_el.inner_text().strip(),
                "company": company_el.inner_text().strip(),
                "location": location_el.inner_text().strip(),
                "status": "saved",
            }

            print("Sending job:", job)
            send_to_backend(job)

        browser.close()

if __name__ == "__main__":
    scrape_indeed()