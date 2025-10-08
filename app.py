from flask import Flask, request, jsonify, render_template, send_file
import os
import tempfile
import logging
import sys
import pathlib

# Add utils to path
sys.path.append(str(pathlib.Path(__file__).parent))

try:
    from utils.scraper import LeadScraper
    from utils.exporter import export_data
except ImportError as e:
    logging.error(f"Import error: {e}")
    # Fallback - define minimal versions if imports fail
    class LeadScraper:
        def scrape_leads(self, search_query, max_results=50):
            return [{
                'name': 'Sample Lead',
                'title': 'Manager',
                'company': 'Sample Company',
                'phone': '+1-555-0123',
                'email': 'contact@sample.com',
                'website': 'https://sample.com',
                'industry': 'Technology',
                'location': 'New York',
                'source': 'Sample'
            }]
    
    def export_data(leads, filename, format_type):
        # Create a simple text file as fallback
        with open(filename, 'w') as f:
            for lead in leads:
                f.write(f"Name: {lead.get('name', '')}\n")
                f.write(f"Phone: {lead.get('phone', '')}\n")
                f.write(f"Email: {lead.get('email', '')}\n\n")

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

@app.route('/')
def index():
    return render_template('index.html')

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
        city = data.get('city', '')
        format_type = data.get('format', 'xlsx')
        
        # Validate input
        if not any([title, industry, country, city]):
            return jsonify({
                'error': 'Please provide at least one search criteria'
            }), 400
        
        # Initialize scraper
        scraper = LeadScraper()
        
        # Generate search query
        search_query_parts = []
        if title:
            search_query_parts.append(title)
        if industry:
            search_query_parts.append(industry)
        if city:
            search_query_parts.append(city)
        if country:
            search_query_parts.append(country)
        
        search_query = " ".join(search_query_parts)
        
        # Scrape leads
        app.logger.info(f"Searching for leads: {search_query}")
        leads = scraper.scrape_leads(search_query, max_results=20)
        
        if not leads:
            return jsonify({
                'error': 'No leads found for the given criteria'
            }), 404
        
        # Export data
        temp_dir = tempfile.gettempdir()
        safe_title = "".join(c for c in title if c.isalnum()) if title else "all"
        safe_industry = "".join(c for c in industry if c.isalnum()) if industry else "all"
        filename = f"leads_{safe_title}_{safe_industry}.{format_type}"
        filepath = os.path.join(temp_dir, filename)
        
        export_data(leads, filepath, format_type)
        
        return jsonify({
            'message': f'Successfully generated {len(leads)} leads',
            'download_url': f'/download/{filename}',
            'leads_count': len(leads)
        })
        
    except Exception as e:
        app.logger.error(f"Error generating leads: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/download/<filename>')
def download_file(filename):
    try:
        temp_dir = tempfile.gettempdir()
        filepath = os.path.join(temp_dir, filename)
        
        if not os.path.exists(filepath):
            return jsonify({'error': 'File not found'}), 404
            
        return send_file(
            filepath,
            as_attachment=True,
            download_name=filename
        )
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)