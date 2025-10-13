from flask import Flask, request, jsonify, render_template, send_file
import os
import tempfile
import logging
import sys
import pathlib

# Add utils to path
sys.path.append(str(pathlib.Path(__file__).parent))

# Import with better error handling
try:
    from utils.scraper import IntelligentLeadScraper
    from utils.exporter import export_data
    logging.info("✅ Successfully imported all modules")
except ImportError as e:
    logging.error(f"❌ Import error: {e}")
    # Create fallback functions
    class IntelligentLeadScraper:
        def scrape_leads(self, search_data, max_results=50):
            logging.info("Using fallback scraper")
            return [{
                'name': 'Test Lead - Check Console',
                'title': 'CEO',
                'company': 'Test Company Ltd',
                'phone': '+1-555-0123',
                'email': 'contact@testcompany.com',
                'website': 'https://testcompany.com',
                'industry': 'Technology',
                'location': 'United States',
                'source': 'Fallback Data'
            }]
    
    def export_data(leads, filename, format_type):
        logging.info("Using fallback exporter")
        import csv
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['Name', 'Title', 'Company', 'Phone', 'Email', 'Website', 'Industry', 'Location', 'Source'])
            for lead in leads:
                writer.writerow([
                    lead.get('name', ''),
                    lead.get('title', ''),
                    lead.get('company', ''),
                    lead.get('phone', ''),
                    lead.get('email', ''),
                    lead.get('website', ''),
                    lead.get('industry', ''),
                    lead.get('location', ''),
                    lead.get('source', '')
                ])

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

# Enhanced country list
COUNTRIES = [
    # European Countries
    "United Kingdom", "Germany", "France", "Italy", "Spain", "Netherlands", 
    "Switzerland", "Sweden", "Norway", "Denmark", "Ireland", "Belgium", 
    "Austria", "Portugal", "Finland", "Poland", "Czech Republic", "Hungary", 
    "Romania", "Greece",
    
    # Wealthy Asian Countries
    "Japan", "South Korea", "Singapore", "Hong Kong", "Taiwan", 
    "United Arab Emirates", "Qatar", "Saudi Arabia", "Israel", "Malaysia",
    
    # Others
    "United States", "Canada", "Australia", "India", "Brazil", "Mexico"
]

JOB_TITLES = [
    "CEO", "CFO", "CTO", "CMO", "COO", "President", "Vice President",
    "Director", "Manager", "Senior Manager", "Executive Director",
    "Managing Director", "Partner", "Owner", "Founder", "Board Member",
    "Head of Department", "Team Lead", "Supervisor"
]

INDUSTRIES = [
    "Technology", "Healthcare", "Finance", "Education", "Real Estate",
    "Manufacturing", "Retail", "Construction", "Transportation",
    "Hospitality", "Energy", "Telecommunications", "Marketing",
    "Consulting", "Legal", "Insurance", "Pharmaceuticals"
]

@app.route('/')
def index():
    return render_template('index.html', 
                         countries=COUNTRIES, 
                         job_titles=JOB_TITLES,
                         industries=INDUSTRIES)

@app.route('/generate-leads', methods=['POST'])
def generate_leads():
    try:
        # Get search criteria
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No JSON data provided'}), 400
            
        title = data.get('title', '')
        industry = data.get('industry', '')
        country = data.get('country', '')
        website_url = data.get('website_url', '')
        format_type = data.get('format', 'xlsx')
        
        # Validate input
        if not any([title, industry, country, website_url]):
            return jsonify({
                'error': 'Please provide at least one search criteria'
            }), 400
        
        # Initialize scraper
        scraper = IntelligentLeadScraper()
        
        # Prepare search data
        search_data = {
            'title': title,
            'industry': industry,
            'country': country,
            'website_url': website_url
        }
        
        # Scrape leads
        app.logger.info(f"🔍 Searching for leads: {search_data}")
        leads = scraper.scrape_leads(search_data, max_results=50)
        
        if not leads:
            return jsonify({
                'error': 'No leads found for the given criteria. Try different search terms.'
            }), 404
        
        # Export data
        temp_dir = tempfile.gettempdir()
        safe_title = "".join(c for c in title if c.isalnum()) if title else "all"
        safe_industry = "".join(c for c in industry if c.isalnum()) if industry else "all"
        filename = f"leads_{safe_title}_{safe_industry}.{format_type}"
        filepath = os.path.join(temp_dir, filename)
        
        app.logger.info(f"💾 Exporting {len(leads)} leads to {filename}")
        export_data(leads, filepath, format_type)
        
        return jsonify({
            'message': f'✅ Successfully generated {len(leads)} leads',
            'download_url': f'/download/{filename}',
            'leads_count': len(leads),
            'leads_preview': leads[:5]  # Preview first 5 leads
        })
        
    except Exception as e:
        app.logger.error(f"❌ Error generating leads: {str(e)}")
        return jsonify({'error': f'Internal server error: {str(e)}'}), 500

@app.route('/download/<filename>')
def download_file(filename):
    try:
        temp_dir = tempfile.gettempdir()
        filepath = os.path.join(temp_dir, filename)
        
        if not os.path.exists(filepath):
            return jsonify({'error': 'File not found. It may have expired.'}), 404
            
        return send_file(
            filepath,
            as_attachment=True,
            download_name=filename
        )
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/health')
def health_check():
    return jsonify({'status': 'healthy', 'message': 'Lead Generator is running'})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.logger.info(f"🚀 Starting Lead Generator on port {port}")
    app.run(host='0.0.0.0', port=port, debug=False)