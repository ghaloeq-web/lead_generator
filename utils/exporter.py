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
        return True
    except ImportError:
        # Fallback to CSV if openpyxl not available
        export_csv(leads, filename.replace('.xlsx', '.csv'))
        return False
    except Exception as e:
        print(f"Error exporting to XLSX: {e}")
        export_csv(leads, filename.replace('.xlsx', '.csv'))
        return False

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
        return True
    except ImportError:
        export_txt(leads, filename.replace('.pdf', '.txt'))
        return False
    except Exception as e:
        print(f"Error exporting to PDF: {e}")
        export_txt(leads, filename.replace('.pdf', '.txt'))
        return False

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
                    # Fix: Properly set name components
                    names = lead['name'].split(' ', 1)
                    if len(names) == 1:
                        vcard.n.value = vobject.vcard.Name(family=names[0], given='')
                    else:
                        vcard.n.value = vobject.vcard.Name(family=names[1], given=names[0])
                
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
                
                # Add note with additional info
                note_parts = []
                if lead.get('industry'):
                    note_parts.append(f"Industry: {lead['industry']}")
                if lead.get('location'):
                    note_parts.append(f"Location: {lead['location']}")
                if lead.get('source'):
                    note_parts.append(f"Source: {lead['source']}")
                
                if note_parts:
                    vcard.add('note')
                    vcard.note.value = '; '.join(note_parts)
                
                f.write(vcard.serialize())
                f.write('\n')
        return True
    except ImportError:
        export_txt(leads, filename.replace('.vcf', '.txt'))
        return False
    except Exception as e:
        print(f"Error exporting to VCF: {e}")
        export_txt(leads, filename.replace('.vcf', '.txt'))
        return False

def export_csv(leads, filename):
    """Export leads to CSV format"""
    try:
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
        return True
    except Exception as e:
        print(f"Error exporting to CSV: {e}")
        return False

def export_txt(leads, filename):
    """Export leads to simple text format"""
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            f.write("BUSINESS LEADS REPORT\n")
            f.write("=" * 50 + "\n\n")
            
            for i, lead in enumerate(leads, 1):
                f.write(f"LEAD #{i}\n")
                f.write("-" * 30 + "\n")
                f.write(f"Name: {lead.get('name', 'N/A')}\n")
                f.write(f"Title: {lead.get('title', 'N/A')}\n")
                f.write(f"Company: {lead.get('company', 'N/A')}\n")
                f.write(f"Phone: {lead.get('phone', 'N/A')}\n")
                f.write(f"Email: {lead.get('email', 'N/A')}\n")
                f.write(f"Website: {lead.get('website', 'N/A')}\n")
                f.write(f"Industry: {lead.get('industry', 'N/A')}\n")
                f.write(f"Location: {lead.get('location', 'N/A')}\n")
                f.write(f"Source: {lead.get('source', 'N/A')}\n")
                f.write("\n" + "=" * 50 + "\n\n")
        return True
    except Exception as e:
        print(f"Error exporting to TXT: {e}")
        return False

def export_data(leads, filename, format_type):
    """Main export function"""
    try:
        # Create directory if needed (FIXED LINE)
        directory = os.path.dirname(filename)
        if directory and not os.path.exists(directory):
            os.makedirs(directory, exist_ok=True)
        
        # Export based on format
        if format_type == 'xlsx':
            return export_xlsx(leads, filename)
        elif format_type == 'pdf':
            return export_pdf(leads, filename)
        elif format_type == 'vcf':
            return export_vcf(leads, filename)
        elif format_type == 'csv':
            return export_csv(leads, filename)
        elif format_type == 'txt':
            return export_txt(leads, filename)
        else:
            # Default to CSV
            new_filename = filename
            for ext in ['.xlsx', '.pdf', '.vcf']:
                if filename.endswith(ext):
                    new_filename = filename.replace(ext, '.csv')
                    break
            return export_csv(leads, new_filename)
            
    except Exception as e:
        print(f"Error in export_data: {e}")
        # Last resort - try CSV
        try:
            csv_filename = 'leads_export.csv'
            return export_csv(leads, csv_filename)
        except:
            return False