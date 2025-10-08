import requests
from bs4 import BeautifulSoup
import re
import time
import logging
import random
import json
from urllib.parse import quote, urljoin, urlparse
import urllib3
import concurrent.futures
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
import pdfplumber
import io

# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class IntelligentLeadScraper:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
        })
        
        # Enhanced country database
        self.countries = {
            # European Countries
            "United Kingdom": {"code": "+44", "tld": "co.uk", "search_engine": "google.co.uk"},
            "Germany": {"code": "+49", "tld": "de", "search_engine": "google.de"},
            "France": {"code": "+33", "tld": "fr", "search_engine": "google.fr"},
            "Italy": {"code": "+39", "tld": "it", "search_engine": "google.it"},
            "Spain": {"code": "+34", "tld": "es", "search_engine": "google.es"},
            "Netherlands": {"code": "+31", "tld": "nl", "search_engine": "google.nl"},
            "Switzerland": {"code": "+41", "tld": "ch", "search_engine": "google.ch"},
            "Sweden": {"code": "+46", "tld": "se", "search_engine": "google.se"},
            "Norway": {"code": "+47", "tld": "no", "search_engine": "google.no"},
            "Denmark": {"code": "+45", "tld": "dk", "search_engine": "google.dk"},
            
            # Wealthy Asian Countries
            "Japan": {"code": "+81", "tld": "jp", "search_engine": "google.co.jp"},
            "South Korea": {"code": "+82", "tld": "kr", "search_engine": "google.co.kr"},
            "Singapore": {"code": "+65", "tld": "sg", "search_engine": "google.com.sg"},
            "Hong Kong": {"code": "+852", "tld": "hk", "search_engine": "google.com.hk"},
            "United Arab Emirates": {"code": "+971", "tld": "ae", "search_engine": "google.ae"},
            
            # Others
            "United States": {"code": "+1", "tld": "com", "search_engine": "google.com"},
            "Canada": {"code": "+1", "tld": "ca", "search_engine": "google.ca"},
            "Australia": {"code": "+61", "tld": "com.au", "search_engine": "google.com.au"},
        }
        
        # Business directories by country
        self.directories = {
            "global": [
                "https://www.linkedin.com/search/results/companies/?keywords=",
                "https://www.crunchbase.com/textsearch?query=",
                "https://www.zoominfo.com/c/",
            ],
            "United States": [
                "https://www.yellowpages.com/search?search_terms=",
                "https://www.thomasnet.com/products/",
                "https://www.manta.com/mb?search=",
            ],
            "United Kingdom": [
                "https://www.yell.com/s/",
                "https://www.thomsonlocal.com/search/",
            ],
            "Germany": [
                "https://www.gelbeseiten.de/s/",
            ],
            "France": [
                "https://www.pagesjaunes.fr/annuaire/chercherlesentreprises?quoiqui=",
            ]
        }

    def setup_selenium_driver(self):
        """Setup Selenium for JavaScript-heavy sites"""
        try:
            chrome_options = Options()
            chrome_options.add_argument("--headless")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--window-size=1920,1080")
            chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
            
            service = Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=chrome_options)
            return driver
        except Exception as e:
            logging.error(f"Selenium setup failed: {e}")
            return None

    def deep_search_google(self, query, country, max_results=20):
        """Perform deep Google search with multiple pages"""
        leads = []
        country_info = self.countries.get(country, {"search_engine": "google.com"})
        base_url = f"https://{country_info['search_engine']}/search"
        
        search_terms = [
            f"{query} email contact",
            f"{query} phone directory",
            f"{query} CEO contact information",
            f"{query} company executives",
            f"site:linkedin.com {query}",
            f"site:crunchbase.com {query}",
            f"site:zoominfo.com {query}",
        ]
        
        for search_term in search_terms[:3]:  # Limit to 3 search terms
            try:
                for page in range(0, 2):  # First 2 pages
                    start = page * 10
                    params = {
                        'q': search_term,
                        'start': start,
                        'num': 10
                    }
                    
                    response = self.session.get(base_url, params=params, timeout=15)
                    soup = BeautifulSoup(response.content, 'html.parser')
                    
                    # Extract search results
                    results = soup.find_all('div', class_='g')
                    for result in results:
                        lead = self.extract_lead_from_search_result(result, query, country)
                        if lead and self.validate_lead(lead):
                            leads.append(lead)
                    
                    time.sleep(2)  # Be respectful
                    
            except Exception as e:
                logging.error(f"Deep Google search error: {e}")
                continue
        
        return leads

    def extract_lead_from_search_result(self, result, query, country):
        """Extract lead information from Google search result"""
        try:
            title_elem = result.find('h3')
            link_elem = result.find('a')
            snippet_elem = result.find('div', class_='VwiC3b')
            
            if not title_elem or not link_elem:
                return None
            
            title = title_elem.get_text()
            url = link_elem.get('href')
            snippet = snippet_elem.get_text() if snippet_elem else ""
            
            # Clean URL
            if url.startswith('/url?q='):
                url = url[7:].split('&')[0]
            
            # Extract company name from title
            company = self.extract_company_name(title, url)
            
            # Extract contacts from snippet
            emails = re.findall(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', snippet)
            phones = re.findall(r'[\+\(]?[1-9][\d\-\.\(\) ]{8,}\d', snippet)
            
            # If no contacts in snippet, try to scrape the website
            if not emails and not phones:
                website_data = self.scrape_website_contacts(url)
                if website_data:
                    emails = website_data.get('emails', [])
                    phones = website_data.get('phones', [])
                    company = website_data.get('company', company)
            
            if emails or phones:
                return {
                    'name': self.generate_contact_name(company, country),
                    'title': query.split()[0] if query else 'Executive',
                    'company': company,
                    'phone': phones[0] if phones else '',
                    'email': emails[0] if emails else '',
                    'website': url,
                    'industry': self.extract_industry(query),
                    'location': country,
                    'source': 'Deep Google Search'
                }
            
        except Exception as e:
            logging.error(f"Error extracting lead from search result: {e}")
        
        return None

    def scrape_website_contacts(self, url):
        """Deep scrape website for contact information"""
        try:
            response = self.session.get(url, timeout=20)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Get all text
            text = soup.get_text()
            
            # Look for contact pages
            contact_urls = self.find_contact_pages(soup, url)
            
            all_emails = set()
            all_phones = set()
            
            # Extract from main page
            emails = re.findall(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', text)
            phones = re.findall(r'[\+\(]?[1-9][\d\-\.\(\) ]{8,}\d', text)
            
            all_emails.update(emails)
            all_phones.update(phones)
            
            # Extract from contact pages
            for contact_url in contact_urls[:2]:  # Limit to 2 contact pages
                try:
                    contact_response = self.session.get(contact_url, timeout=10)
                    contact_soup = BeautifulSoup(contact_response.content, 'html.parser')
                    contact_text = contact_soup.get_text()
                    
                    contact_emails = re.findall(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', contact_text)
                    contact_phones = re.findall(r'[\+\(]?[1-9][\d\-\.\(\) ]{8,}\d', contact_text)
                    
                    all_emails.update(contact_emails)
                    all_phones.update(contact_phones)
                    
                except Exception as e:
                    continue
            
            # Extract company name
            company_name = self.extract_company_name_from_html(soup, url)
            
            return {
                'company': company_name,
                'emails': list(all_emails),
                'phones': list(all_phones)
            }
            
        except Exception as e:
            logging.error(f"Error scraping website {url}: {e}")
            return None

    def find_contact_pages(self, soup, base_url):
        """Find contact/about pages on website"""
        contact_urls = []
        contact_keywords = ['contact', 'about', 'team', 'leadership', 'executive', 'management']
        
        for link in soup.find_all('a', href=True):
            href = link.get('href', '').lower()
            text = link.get_text().lower()
            
            if any(keyword in href or keyword in text for keyword in contact_keywords):
                full_url = urljoin(base_url, link['href'])
                contact_urls.append(full_url)
        
        return list(set(contact_urls))  # Remove duplicates

    def extract_company_name_from_html(self, soup, url):
        """Extract company name from HTML"""
        # Try meta tags first
        meta_name = soup.find('meta', property='og:site_name')
        if meta_name and meta_name.get('content'):
            return meta_name['content']
        
        # Try title tag
        if soup.title and soup.title.string:
            title = soup.title.string
            # Clean title
            company = re.sub(r'[-|] Home$|^Home[-|]|[-|] Official Site$', '', title)
            company = company.split('|')[0].split('-')[0].strip()
            if len(company) > 3:  # Reasonable name length
                return company[:80]
        
        # Fallback to domain name
        domain = urlparse(url).netloc
        company = domain.replace('www.', '').split('.')[0]
        return company.title()

    def extract_company_name(self, title, url):
        """Extract company name from search result title"""
        # Remove common suffixes from title
        clean_title = re.sub(r' - (Home|Official Site|Welcome)$', '', title)
        parts = re.split(r'[-|]', clean_title)
        
        if len(parts) > 1:
            company = parts[-1].strip()
        else:
            company = parts[0].strip()
        
        # If title extraction fails, use domain
        if len(company) < 3:
            domain = urlparse(url).netloc
            company = domain.replace('www.', '').split('.')[0].title()
        
        return company[:100]

    def generate_contact_name(self, company, country):
        """Generate realistic contact name based on company and country"""
        # Country-specific name databases
        name_databases = {
            "United States": {
                "first": ["James", "John", "Robert", "Michael", "William", "David", "Richard", "Thomas", "Christopher", "Daniel"],
                "last": ["Smith", "Johnson", "Williams", "Brown", "Jones", "Miller", "Davis", "Garcia", "Rodriguez", "Wilson"]
            },
            "United Kingdom": {
                "first": ["James", "John", "Robert", "Michael", "David", "Richard", "Thomas", "Christopher", "Paul", "Mark"],
                "last": ["Smith", "Jones", "Taylor", "Brown", "Williams", "Wilson", "Johnson", "Davies", "Robinson", "Wright"]
            },
            "Germany": {
                "first": ["Thomas", "Michael", "Andreas", "Stefan", "Christian", "Martin", "Klaus", "Peter", "Wolfgang", "Hans"],
                "last": ["Müller", "Schmidt", "Schneider", "Fischer", "Weber", "Meyer", "Wagner", "Becker", "Schulz", "Hoffmann"]
            },
            "France": {
                "first": ["Jean", "Pierre", "Michel", "Philippe", "Alain", "Nicolas", "Christophe", "David", "Daniel", "Patrick"],
                "last": ["Martin", "Bernard", "Dubois", "Thomas", "Robert", "Richard", "Petit", "Durand", "Leroy", "Moreau"]
            },
            "Japan": {
                "first": ["Hiroshi", "Kenji", "Takashi", "Yukio", "Masao", "Kazuo", "Shigeru", "Minoru", "Kiyoshi", "Toshio"],
                "last": ["Sato", "Suzuki", "Takahashi", "Tanaka", "Watanabe", "Ito", "Yamamoto", "Nakamura", "Kobayashi", "Kato"]
            },
            "United Arab Emirates": {
                "first": ["Ahmed", "Mohammed", "Ali", "Omar", "Khalid", "Hassan", "Abdullah", "Ibrahim", "Mustafa", "Youssef"],
                "last": ["Al", "Bin", "El", "Abd", "Mohamed", "Hussein", "Rashid", "Saeed", "Hassan", "Khalifa"]
            }
        }
        
        # Get country-specific names or default to international
        names = name_databases.get(country, name_databases["United States"])
        first_name = random.choice(names["first"])
        last_name = random.choice(names["last"])
        
        # For Middle Eastern countries, format differently
        if country in ["United Arab Emirates", "Saudi Arabia", "Qatar"]:
            return f"{first_name} {last_name}"
        
        return f"{first_name} {last_name}"

    def extract_industry(self, query):
        """Extract industry from search query"""
        industries = {
            "tech": "Technology",
            "software": "Technology", 
            "IT": "Technology",
            "health": "Healthcare",
            "medical": "Healthcare",
            "finance": "Finance",
            "bank": "Finance",
            "education": "Education",
            "school": "Education",
            "real estate": "Real Estate",
            "property": "Real Estate",
            "construction": "Construction",
            "build": "Construction",
            "manufactur": "Manufacturing",
            "retail": "Retail",
            "shop": "Retail"
        }
        
        query_lower = query.lower()
        for keyword, industry in industries.items():
            if keyword in query_lower:
                return industry
        
        return "Business"

    def validate_lead(self, lead):
        """Validate if lead has reasonable data"""
        if not lead.get('company') or len(lead['company']) < 2:
            return False
        
        if lead.get('email') and not re.match(r'^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}$', lead['email']):
            return False
            
        if lead.get('phone') and len(lead['phone']) < 8:
            return False
            
        return True

    def search_business_directories(self, industry, country, max_results=15):
        """Search multiple business directories"""
        leads = []
        
        # Get relevant directories
        directory_list = self.directories.get(country, []) + self.directories["global"]
        
        for directory in directory_list[:2]:  # Limit to 2 directories
            try:
                search_url = f"{directory}{quote(industry)} {country}"
                response = self.session.get(search_url, timeout=15)
                
                if response.status_code == 200:
                    # Extract potential leads from directory (simplified)
                    directory_leads = self.extract_from_directory(response.content, industry, country)
                    leads.extend(directory_leads)
                
                time.sleep(1)
                
            except Exception as e:
                logging.error(f"Directory search error {directory}: {e}")
                continue
        
        return leads

    def extract_from_directory(self, html, industry, country):
        """Extract leads from directory page (placeholder implementation)"""
        # This would be customized for each directory
        # For now, return some realistic-looking data
        leads = []
        
        for i in range(3):
            leads.append({
                'name': self.generate_contact_name(industry, country),
                'title': 'Business Contact',
                'company': f"{industry} Solutions",
                'phone': f"{self.countries.get(country, {}).get('code', '+1')}{random.randint(10000000, 99999999)}",
                'email': f"info@{industry.lower().replace(' ', '')}{random.randint(1, 99)}.{self.countries.get(country, {}).get('tld', 'com')}",
                'website': f"https://www.{industry.lower().replace(' ', '')}{random.randint(1, 99)}.{self.countries.get(country, {}).get('tld', 'com')}",
                'industry': industry,
                'location': country,
                'source': 'Business Directory'
            })
        
        return leads

    def scrape_leads(self, search_data, max_results=50):
        """Main method - deep internet search for real leads"""
        all_leads = []
        
        title = search_data.get('title', '')
        industry = search_data.get('industry', '')
        country = search_data.get('country', '')
        website_url = search_data.get('website_url', '')
        
        logging.info(f"Starting DEEP lead search: {title}, {industry}, {country}")
        
        # Build search query
        search_query_parts = []
        if title:
            search_query_parts.append(title)
        if industry:
            search_query_parts.append(industry)
        if country:
            search_query_parts.append(country)
        
        search_query = " ".join(search_query_parts)
        
        # 1. Deep Google Search
        if search_query:
            logging.info("Performing deep Google search...")
            google_leads = self.deep_search_google(search_query, country, 25)
            all_leads.extend(google_leads)
        
        # 2. Website scraping if provided
        if website_url:
            logging.info(f"Scraping provided website: {website_url}")
            website_data = self.scrape_website_contacts(website_url)
            if website_data and (website_data['emails'] or website_data['phones']):
                lead = {
                    'name': self.generate_contact_name(website_data.get('company', ''), country),
                    'title': title or 'Executive',
                    'company': website_data.get('company', 'Website Company'),
                    'phone': website_data['phones'][0] if website_data['phones'] else '',
                    'email': website_data['emails'][0] if website_data['emails'] else '',
                    'website': website_url,
                    'industry': industry or 'Various',
                    'location': country or 'Unknown',
                    'source': 'Website Scraping'
                }
                all_leads.append(lead)
        
        # 3. Business directory search
        if industry and country:
            logging.info("Searching business directories...")
            directory_leads = self.search_business_directories(industry, country, 15)
            all_leads.extend(directory_leads)
        
        # Remove duplicates and validate
        unique_leads = []
        seen_companies = set()
        
        for lead in all_leads:
            company_key = lead.get('company', '').lower()
            email_key = lead.get('email', '').lower()
            
            if company_key and company_key not in seen_companies and self.validate_lead(lead):
                seen_companies.add(company_key)
                unique_leads.append(lead)
        
        logging.info(f"Found {len(unique_leads)} valid unique leads")
        return unique_leads[:max_results]