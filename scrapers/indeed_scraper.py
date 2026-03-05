from playwright.sync_api import sync_playwright
import requests

API_URL = "https://job-tracker-backend-whae.onrender.com/jobs"

def send_to_backend(job):
    resp = requests.post(API_URL, json=job)
    print(resp.status_code, resp.json())

def scrape_indeed():
    print("Scraper started")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        # Load all jobs in the US
        page.goto("https://www.indeed.com/jobs?q=&l=United+States")

        # Wait for job cards to load
        page.wait_for_selector("div.job_seen_beacon")

        cards = page.query_selector_all("div.job_seen_beacon")
        print("Found job cards:", len(cards))

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
