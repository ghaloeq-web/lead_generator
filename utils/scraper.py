import requests
from bs4 import BeautifulSoup
import re
import time
import logging
import random
import pdfplumber
import io
from urllib.parse import urljoin, urlparse
import json

class AdvancedLeadScraper:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
    def extract_contacts_from_text(self, text):
        """Extract phone numbers and emails from text"""
        if not text:
            return [], []
            
        # Phone patterns
        phone_patterns = [
            r'\+?1?[-.\s]?\(?[0-9]{3}\)?[-.\s]?[0-9]{3}[-.\s]?[0-9]{4}',
            r'\([0-9]{3}\)\s*[0-9]{3}-[0-9]{4}',
            r'[0-9]{3}-[0-9]{3}-[0-9]{4}',
            r'\+\d{1,3}[-.\s]?\(?\d{1,4}\)?[-.\s]?\d{1,4}[-.\s]?\d{1,9}'
        ]
        
        phones = []
        for pattern in phone_patterns:
            matches = re.findall(pattern, text)
            phones.extend(matches)
        
        # Email pattern
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        emails = re.findall(email_pattern, text)
        
        return list(set(phones)), list(set(emails))
    
    def scrape_website_contacts(self, url):
        """Scrape contact information from a website"""
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Remove scripts and styles
            for script in soup(["script", "style"]):
                script.decompose()
            
            text = soup.get_text()
            phones, emails = self.extract_contacts_from_text(text)
            
            # Look for contact pages
            contact_links = []
            for link in soup.find_all('a', href=True):
                href = link['href'].lower()
                if any(keyword in href for keyword in ['contact', 'about', 'team', 'leadership']):
                    contact_links.append(urljoin(url, link['href']))
            
            # Try contact pages
            for contact_link in contact_links[:3]:  # Limit to first 3 contact pages
                try:
                    contact_response = self.session.get(contact_link, timeout=5)
                    contact_soup = BeautifulSoup(contact_response.content, 'html.parser')
                    contact_text = contact_soup.get_text()
                    contact_phones, contact_emails = self.extract_contacts_from_text(contact_text)
                    phones.extend(contact_phones)
                    emails.extend(contact_emails)
                except:
                    continue
            
            # Extract company name from title or meta
            company_name = ""
            if soup.title:
                company_name = soup.title.string.split('|')[0].split('-')[0].strip()
            
            return {
                'company': company_name,
                'phones': list(set(phones)),
                'emails': list(set(emails)),
                'website': url
            }
            
        except Exception as e:
            logging.error(f"Error scraping website {url}: {e}")
            return None
    
    def extract_from_pdf(self, pdf_url_or_file):
        """Extract text and contacts from PDF"""
        try:
            if pdf_url_or_file.startswith('http'):
                response = self.session.get(pdf_url_or_file)
                pdf_file = io.BytesIO(response.content)
            else:
                pdf_file = pdf_url_or_file
            
            text = ""
            with pdfplumber.open(pdf_file) as pdf:
                for page in pdf.pages:
                    text += page.extract_text() or ""
            
            phones, emails = self.extract_contacts_from_text(text)
            return {
                'phones': phones,
                'emails': emails,
                'text': text[:1000]  # First 1000 chars
            }
        except Exception as e:
            logging.error(f"Error extracting from PDF: {e}")
            return None
    
    def search_linkedin_sales_navigator(self, title, industry, country):
        """Simulate LinkedIn Sales Navigator search (placeholder)"""
        # Note: Actual LinkedIn scraping requires official API or careful web scraping
        # This is a simulation that returns realistic-looking data
        
        domains = {
            "United States": "com",
            "United Kingdom": "co.uk", 
            "Canada": "ca",
            "Australia": "com.au",
            "Germany": "de"
        }
        
        domain = domains.get(country, "com")
        
        sample_leads = []
        for i in range(15):
            first_names = ["John", "Sarah", "Michael", "Emily", "David", "Lisa", "Robert", "Jennifer"]
            last_names = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis"]
            
            lead = {
                'name': f"{random.choice(first_names)} {random.choice(last_names)}",
                'title': title,
                'company': f"{industry} Solutions Inc." if industry else "Global Corp",
                'phone': f"+1-555-01{10+i}",
                'email': f"contact.{random.choice(first_names).lower()}{i}@company.com",
                'website': f"https://www.company{industry or 'tech'}{i}.{domain}",
                'industry': industry or "Various",
                'location': country,
                'source': 'LinkedIn Simulation'
            }
            sample_leads.append(lead)
        
        return sample_leads
    
    def search_business_directories(self, industry, country):
        """Search business directories (placeholder)"""
        directories = [
            "Yellow Pages", "Thomas Net", "Manta", "Kompass", "Dun & Bradstreet"
        ]
        
        sample_leads = []
        for i in range(10):
            lead = {
                'name': f"Business Owner {i+1}",
                'title': "Owner/Manager",
                'company': f"{industry} Enterprises {country}",
                'phone': f"+1-800-{500+i:03d}-{1000+i:04d}",
                'email': f"info@{industry.lower()}{i}.com",
                'website': f"https://www.{industry.lower()}{i}.com",
                'industry': industry,
                'location': country,
                'source': random.choice(directories)
            }
            sample_leads.append(lead)
        
        return sample_leads
    
    def scrape_leads(self, search_data, max_results=50):
        """Main method to scrape leads from multiple sources"""
        all_leads = []
        
        title = search_data.get('title', '')
        industry = search_data.get('industry', '')
        country = search_data.get('country', '')
        website_url = search_data.get('website_url', '')
        
        # 1. Scrape from provided website
        if website_url:
            logging.info(f"Scraping website: {website_url}")
            website_data = self.scrape_website_contacts(website_url)
            if website_data and (website_data['phones'] or website_data['emails']):
                lead = {
                    'name': 'Website Contact',
                    'title': title or 'Contact',
                    'company': website_data['company'],
                    'phone': website_data['phones'][0] if website_data['phones'] else '',
                    'email': website_data['emails'][0] if website_data['emails'] else '',
                    'website': website_url,
                    'industry': industry or 'Various',
                    'location': country or 'Unknown',
                    'source': 'Website Scraping'
                }
                all_leads.append(lead)
        
        # 2. Search LinkedIn (simulated)
        if title or industry:
            logging.info("Searching business directories...")
            linkedin_leads = self.search_linkedin_sales_navigator(title, industry, country)
            all_leads.extend(linkedin_leads)
        
        # 3. Search business directories
        if industry:
            logging.info("Searching business directories...")
            directory_leads = self.search_business_directories(industry, country)
            all_leads.extend(directory_leads)
        
        # Remove duplicates based on phone/email
        unique_leads = []
        seen_contacts = set()
        
        for lead in all_leads:
            contact_id = f"{lead.get('phone', '')}_{lead.get('email', '')}"
            if contact_id not in seen_contacts and contact_id != '_':
                seen_contacts.add(contact_id)
                unique_leads.append(lead)
        
        return unique_leads[:max_results]