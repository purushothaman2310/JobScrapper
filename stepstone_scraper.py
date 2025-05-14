import requests
from bs4 import BeautifulSoup
import smtplib
from email.mime.text import MIMEText
import os
import datetime

KEYWORDS = ['codesys', 'iec61131-3']
EMAIL_FROM = os.getenv('EMAIL_FROM')
EMAIL_TO = os.getenv('EMAIL_TO')
EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD')
SMTP_SERVER = 'smtp.gmail.com'
SMTP_PORT = 587

def fetch_stepstone_jobs(keyword):
    url = f"https://www.stepstone.de/jobs/{keyword.replace(' ', '-')}.html"
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers)

    soup = BeautifulSoup(response.text, 'html.parser')
    job_cards = soup.find_all('article', class_='ResultlistItem')

    jobs = []
    for card in job_cards[:10]:  # limit to top 10 results
        title_tag = card.find('a', class_='ResultlistItem-title')
        if title_tag:
            job = {
                'title': title_tag.get_text(strip=True),
                'link': 'https://www.stepstone.de' + title_tag['href'],
                'company': card.find('div', class_='ResultlistItem-subtitle').get_text(strip=True) if card.find('div', class_='ResultlistItem-subtitle') else '',
                'location': card.find('div', class_='ResultlistItem-location').get_text(strip=True) if card.find('div', class_='ResultlistItem-location') else ''
            }
            jobs.append(job)
    return jobs

def send_email(jobs_by_keyword):
    html = "<h2>📌 Daily Job Alert – StepStone</h2>"
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
        all_jobs[keyword] = fetch_stepstone_jobs(keyword)
    send_email(all_jobs)
