import requests
from bs4 import BeautifulSoup

API_URL = "https://job-tracker-backend-whae.onrender.com/jobs"

def send_to_backend(job):
    resp = requests.post(API_URL, json=job)
    print(resp.status_code, resp.json())

def scrape_indeed():
    search_url = (
        "https://www.indeed.com/jobs"
        "?q=data+analyst&l=United+States&sc=0kf%3Aexplvl(ENTRY_LEVEL)%3B"
    )

    page = requests.get(search_url, headers={"User-Agent": "Mozilla/5.0"})
    soup = BeautifulSoup(page.text, "html.parser")

    job_cards = soup.select("div.job_seen_beacon")

    for card in job_cards:
        title_el = card.select_one("h2 span")
        company_el = card.select_one("span.companyName")
        location_el = card.select_one("div.companyLocation")
        link_el = card.select_one("a")

        if not (title_el and company_el and location_el and link_el):
            continue

        job = {
            "title": title_el.get_text(strip=True),
            "company": company_el.get_text(strip=True),
            "location": location_el.get_text(strip=True),
            "status": "saved",
        }

        print("Sending job:", job)
        send_to_backend(job)

if __name__ == "__main__":
    scrape_indeed()