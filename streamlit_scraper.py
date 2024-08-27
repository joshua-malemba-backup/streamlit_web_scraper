import os
import re
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import streamlit as st

class EmailScraper:
    def __init__(self):
        self.urls = []

    def browse_file(self):
        uploaded_file = st.file_uploader("Upload a file", type=["csv"], key='file_uploader')
        if uploaded_file is not None:
            file_content = uploaded_file.read().decode('utf-8')
            self.urls = [line.strip() for line in file_content.splitlines() if line.strip()]
            st.session_state['urls'] = self.urls

    def start_scraping(self, urls):
        emails_by_url = {}
        options = Options()
        options.add_argument('--headless')
        options.add_argument('--disable-gpu')
        options.add_argument('--no-sandbox')
        driver = webdriver.Chrome(options=options)

        try:
            for url in urls:
                try:
                    driver.get(url)
                    WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.TAG_NAME, "body")))

                    page_source = driver.page_source
                    soup = BeautifulSoup(page_source, 'html.parser')
                    regex = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b")
                    page_text = soup.get_text()
                    list_of_emails = re.findall(regex, page_text)

                    emails_by_url[url] = list_of_emails
                except Exception as e:
                    continue

            st.session_state['emails_by_url'] = emails_by_url
            return emails_by_url

        finally:
            driver.quit()

    def display_emails(self, emails_by_url):
        if not emails_by_url:
            st.write("No emails found.")
        else:
            for url, emails in emails_by_url.items():
                st.write(f"**Emails from {url}:**")
                if emails:
                    for email in emails:
                        st.write(email)
                else:
                    st.write("No emails found on this page.")

    def save_emails(self, emails_by_url):
        if not emails_by_url:
            st.warning("No emails to save.")
            return

        save_directory = os.path.expanduser("~")
        file_path = os.path.join(save_directory, "scraped_emails.txt")
        with open(file_path, "a") as file:
            for url, emails in emails_by_url.items():
                file.write(f"Emails from {url}:\n")
                if emails:
                    for email in emails:
                        file.write(email + "\n")
                else:
                    file.write("No emails found on this page.\n")
                file.write("\n")  # Add a blank line between entries for readability

        st.success(f"Emails have been saved in {file_path}.")

# Initialize EmailScraper
scraper = EmailScraper()

st.title("Email Scraper")

# Text input for URLs
input_text = st.text_input("Enter URL or Upload a File (Text file containing URLs):")

# File uploader for browsing files
scraper.browse_file()

# Scrape Emails
if st.button("Scrape Emails"):
    urls = st.session_state.get('urls', [])
    if not input_text and not urls:
        st.warning("Please enter a URL or upload a file.")
    else:
        if input_text:
            urls.append(input_text)
        emails_by_url = scraper.start_scraping(urls)
        scraper.display_emails(emails_by_url)

# Save Emails
if st.button("Save Emails"):
    emails_by_url = st.session_state.get('emails_by_url', {})
    if emails_by_url:
        scraper.save_emails(emails_by_url)
    else:
        st.warning("No emails to save.")
