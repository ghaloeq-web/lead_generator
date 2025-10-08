import requests
from bs4 import BeautifulSoup
import re
import time
import logging
import random

class LeadScraper:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
    def extract_phone_numbers(self, text):
        """Extract phone numbers from text using regex"""
        if not text:
            return []
            
        phone_patterns = [
            r'\+?1?[-.\s]?\(?[0-9]{3}\)?[-.\s]?[0-9]{3}[-.\s]?[0-9]{4}',
            r'\([0-9]{3}\)\s*[0-9]{3}-[0-9]{4}',
            r'[0-9]{3}-[0-9]{3}-[0-9]{4}'
        ]
        
        phones = []
        for pattern in phone_patterns:
            matches = re.findall(pattern, text)
            phones.extend(matches)
        
        return list(set(phones))  # Remove duplicates
    
    def extract_emails(self, text):
        """Extract email addresses from text"""
        if not text:
            return []
            
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        emails = re.findall(email_pattern, text)
        return list(set(emails))
    
    def generate_sample_leads(self, query):
        """Generate sample leads for demonstration"""
        industries = ['Technology', 'Healthcare', 'Finance', 'Education', 'Real Estate']
        cities = ['New York', 'London', 'Tokyo', 'Berlin', 'Paris']
        
        sample_leads = []
        for i in range(10):
            industry = random.choice(industries)
            city = random.choice(cities)
            
            lead = {
                'name': f'John Smith {i+1}',
                'title': query.split()[0] if query else 'Manager',
                'company': f'ABC {industry} Corp',
                'phone': f'+1-555-01{10+i}',
                'email': f'contact{i}@abc{industry.lower()}.com',
                'website': f'https://abc{industry.lower()}{i}.com',
                'industry': industry,
                'location': f'{city}, USA',
                'source': 'Sample Data'
            }
            sample_leads.append(lead)
        
        return sample_leads
    
    def scrape_leads(self, search_query, max_results=20):
        """Main method to scrape leads - uses sample data for demo"""
        logging.info(f"Searching for: {search_query}")
        
        # For demo purposes, return sample data
        # In production, you would implement actual scraping here
        leads = self.generate_sample_leads(search_query)
        
        # Simulate processing time
        time.sleep(2)
        
        return leads[:max_results]