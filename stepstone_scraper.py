import requests
from bs4 import BeautifulSoup
import smtplib
from email.mime.text import MIMEText
import os
import datetime
import time

KEYWORDS = ['codesys', 'iec61131-3']
EMAIL_FROM = os.getenv('EMAIL_FROM')
EMAIL_TO = os.getenv('EMAIL_TO')
EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD')
SMTP_SERVER = 'smtp.gmail.com'
SMTP_PORT = 587

def fetch_indeed_jobs(keyword):
    url = f"https://de.indeed.com/jobs?q={keyword.replace(' ', '+')}&l="
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/90.0 Safari/537.36"
    }

    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"❌ Failed to fetch jobs for keyword: {keyword} – {e}")
        return []

    soup = BeautifulSoup(response.text, 'html.parser')
    job_cards = soup.find_all('a', class_='tapItem')

    jobs = []
    for card in job_cards[:10]:  # limit to top 10 per keyword
        title = card.find('h2', class_='jobTitle')
        company = card.find('span', class_='companyName')
        location = card.find('div', class_='companyLocation')

        if title:
            job = {
                'title': title.get_text(strip=True),
                'link': 'https://de.indeed.com' + card['href'],
                'company': company.get_text(strip=True) if company else '',
                'location': location.get_text(strip=True) if location else ''
            }
            jobs.append(job)
    return jobs

def send_email(jobs_by_keyword):
    html = "<h2>📌 Daily Job Alert – Indeed Germany</h2>"
    for keyword, jobs in jobs_by_keyword.items():
        html += f"<h3>🔍 {keyword}</h3><ul>"
        if jobs:
            for job in jobs:
                html += f"<li><a href='{job['link']}'>{job['title']}</a> – {job['company']} ({job['location']})</li>"
        else:
            html += "<li>No results found.</li>"
        html += "</ul>"

    msg = MIMEText(html, 'html')
    msg['Subject'] = f"📬 {sum(len(j) for j in jobs_by_keyword.values())} New Jobs – {datetime.date.today()}"
    msg['From'] = EMAIL_FROM
    msg['To'] = EMAIL_TO

    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
        server.starttls()
        server.login(EMAIL_FROM, EMAIL_PASSWORD)
        server.sendmail(EMAIL_FROM, EMAIL_TO, msg.as_string())

if __name__ == "__main__":
    all_jobs = {}
    for keyword in KEYWORDS:
        print(f"🔍 Searching: {keyword}")
        time.sleep(1)  # be polite to Indeed
        all_jobs[keyword] = fetch_indeed_jobs(keyword)
    send_email(all_jobs)
