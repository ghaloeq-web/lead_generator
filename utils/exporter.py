import os
import csv

def export_xlsx(leads, filename):
    """Export leads to Excel format"""
    try:
        import openpyxl
        from openpyxl import Workbook
        
        wb = Workbook()
        ws = wb.active
        ws.title = "Leads"
        
        # Headers
        headers = ['Name', 'Title', 'Company', 'Phone', 'Email', 'Website', 'Industry', 'Location', 'Source']
        ws.append(headers)
        
        # Data
        for lead in leads:
            row = [
                lead.get('name', ''),
                lead.get('title', ''),
                lead.get('company', ''),
                lead.get('phone', ''),
                lead.get('email', ''),
                lead.get('website', ''),
                lead.get('industry', ''),
                lead.get('location', ''),
                lead.get('source', '')
            ]
            ws.append(row)
        
        wb.save(filename)
    except ImportError:
        # Fallback to CSV if openpyxl not available
        export_csv(leads, filename.replace('.xlsx', '.csv'))

def export_pdf(leads, filename):
    """Export leads to PDF format"""
    try:
        from fpdf import FPDF
        
        pdf = FPDF()
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.add_page()
        
        # Title
        pdf.set_font('Arial', 'B', 16)
        pdf.cell(0, 10, 'Business Leads Report', 0, 1, 'C')
        pdf.ln(10)
        
        # Content
        for i, lead in enumerate(leads, 1):
            pdf.set_font('Arial', 'B', 12)
            pdf.cell(0, 10, f'Lead #{i}', 0, 1)
            pdf.set_font('Arial', '', 10)
            
            info = [
                f"Name: {lead.get('name', 'N/A')}",
                f"Title: {lead.get('title', 'N/A')}",
                f"Company: {lead.get('company', 'N/A')}",
                f"Phone: {lead.get('phone', 'N/A')}",
                f"Email: {lead.get('email', 'N/A')}",
                f"Website: {lead.get('website', 'N/A')}",
                f"Industry: {lead.get('industry', 'N/A')}",
                f"Location: {lead.get('location', 'N/A')}",
                f"Source: {lead.get('source', 'N/A')}"
            ]
            
            for line in info:
                pdf.cell(0, 6, line, 0, 1)
            pdf.ln(5)
        
        pdf.output(filename)
    except ImportError:
        export_txt(leads, filename.replace('.pdf', '.txt'))

def export_vcf(leads, filename):
    """Export leads to vCard format"""
    try:
        import vobject
        
        with open(filename, 'w', encoding='utf-8') as f:
            for i, lead in enumerate(leads):
                vcard = vobject.vCard()
                
                # Add name
                if lead.get('name'):
                    vcard.add('n')
                    vcard.n.value = vobject.vcard.Name(family=lead['name'], given='')
                
                # Add formatted name
                if lead.get('name'):
                    vcard.add('fn')
                    vcard.fn.value = lead['name']
                
                # Add phone
                if lead.get('phone'):
                    vcard.add('tel')
                    vcard.tel.value = lead['phone']
                    vcard.tel.type_param = 'WORK'
                
                # Add email
                if lead.get('email'):
                    vcard.add('email')
                    vcard.email.value = lead['email']
                    vcard.email.type_param = 'WORK'
                
                # Add organization
                if lead.get('company'):
                    vcard.add('org')
                    vcard.org.value = [lead['company']]
                
                # Add title
                if lead.get('title'):
                    vcard.add('title')
                    vcard.title.value = lead['title']
                
                f.write(vcard.serialize())
                f.write('\n')
    except ImportError:
        export_txt(leads, filename.replace('.vcf', '.txt'))

def export_csv(leads, filename):
    """Export leads to CSV format"""
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

def export_txt(leads, filename):
    """Export leads to simple text format"""
    with open(filename, 'w', encoding='utf-8') as f:
        for i, lead in enumerate(leads, 1):
            f.write(f"Lead #{i}\n")
            f.write(f"Name: {lead.get('name', '')}\n")
            f.write(f"Title: {lead.get('title', '')}\n")
            f.write(f"Company: {lead.get('company', '')}\n")
            f.write(f"Phone: {lead.get('phone', '')}\n")
            f.write(f"Email: {lead.get('email', '')}\n")
            f.write(f"Website: {lead.get('website', '')}\n")
            f.write(f"Industry: {lead.get('industry', '')}\n")
            f.write(f"Location: {lead.get('location', '')}\n")
            f.write(f"Source: {lead.get('source', '')}\n")
            f.write("\n" + "="*50 + "\n\n")

def export_data(leads, filename, format_type):
    """Main export function"""
    os.makedirs(os.path.dirname(filename) if os.path.dirname(filename) else '.', exist_ok=True)
    
    if format_type == 'xlsx':
        export_xlsx(leads, filename)
    elif format_type == 'pdf':
        export_pdf(leads, filename)
    elif format_type == 'vcf':
        export_vcf(leads, filename)
    else:
        # Default to CSV
        export_csv(leads, filename.replace('.xlsx', '.csv').replace('.pdf', '.csv').replace('.vcf', '.csv'))