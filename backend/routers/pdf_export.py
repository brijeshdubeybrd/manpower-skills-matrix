from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate, Table, TableStyle, Paragraph, 
    Spacer, Flowable, KeepTogether, PageBreak
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from io import BytesIO
from datetime import datetime
from typing import List, Dict, Any
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

# --- Constants & Colors (Matching Frontend Tailwind) ---
COLOR_BAND_BG = colors.HexColor('#eff6ff')      # bg-blue-50
COLOR_BAND_TEXT = colors.HexColor('#1e40af')    # text-blue-800
COLOR_BAND_LABEL = colors.HexColor('#2563eb')   # text-blue-600

# Functional (Emerald)
COLOR_FUNC_BG = colors.HexColor('#d1fae5')      # bg-emerald-100
COLOR_FUNC_BORDER = colors.HexColor('#a7f3d0')  # border-emerald-200
COLOR_FUNC_TEXT = colors.HexColor('#047857')    # text-emerald-700
COLOR_FUNC_DOT_ON = colors.HexColor('#34d399')  # bg-emerald-400
COLOR_FUNC_DOT_OFF = colors.HexColor('#e5e7eb') # bg-gray-200

# Leadership (Purple)
COLOR_LEAD_BG = colors.HexColor('#f3e8ff')      # bg-purple-100
COLOR_LEAD_BORDER = colors.HexColor('#e9d5ff')  # border-purple-200
COLOR_LEAD_TEXT = colors.HexColor('#7e22ce')    # text-purple-700
COLOR_LEAD_DOT_ON = colors.HexColor('#c084fc')  # bg-purple-400
COLOR_LEAD_DOT_OFF = colors.HexColor('#e5e7eb') # bg-gray-200

HEADER_RED = colors.HexColor('#CD202C')         # Raymond Red


class ProficiencyDots(Flowable):
    """Draws 5 dots to represent proficiency level"""
    def __init__(self, level, is_leadership=False, size=6, space=2):
        Flowable.__init__(self)
        try:
            self.level = int(level)
        except:
            self.level = 0
        self.is_leadership = is_leadership
        self.size = size
        self.space = space
        self.width = (size * 5) + (space * 4)
        self.height = size + 4 # Padding

    def draw(self):
        self.canv.saveState()
        dot_on = COLOR_LEAD_DOT_ON if self.is_leadership else COLOR_FUNC_DOT_ON
        dot_off = COLOR_LEAD_DOT_OFF
        
        for i in range(1, 6):
            x = (i - 1) * (self.size + self.space)
            y = 2  # Bottom padding
            
            self.canv.setFillColor(dot_on if i <= self.level else dot_off)
            self.canv.setStrokeColor(colors.white) # No border or white border
            self.canv.setLineWidth(0)
            
            # Draw circle
            radius = self.size / 2
            self.canv.circle(x + radius, y + radius, radius, fill=1, stroke=0)
            
        self.canv.restoreState()


def get_band_order():
    return ['Band 1A', 'Band 1B', 'Band 2A', 'Band 2B', 'Band 3', 'Band 4', 'Band 5']


def create_header_footer(canvas, doc):
    canvas.saveState()
    width, height = A4
    
    # Header Bar
    canvas.setFillColor(HEADER_RED)
    canvas.rect(0, height - 15*mm, width, 15*mm, fill=1, stroke=0)
    
    # Header Text
    canvas.setFont('Helvetica-Bold', 12)
    canvas.setFillColor(colors.white)
    canvas.drawString(15*mm, height - 10*mm, "Manpower & Skills Matrix Report")
    
    canvas.setFont('Helvetica', 9)
    canvas.drawRightString(width - 15*mm, height - 10*mm, 
                          f"Generated: {datetime.now().strftime('%d %b %Y, %H:%M')}")
    
    # Footer
    canvas.setFillColor(colors.black)
    canvas.setFont('Helvetica', 8)
    canvas.drawCentredString(width/2, 10*mm, f"Page {doc.page}")
    
    canvas.restoreState()


def create_skill_cell_content(skill, is_leadership, width):
    """Create a mini-table for a single skill cell"""
    if not skill:
        return ""
        
    dots = ProficiencyDots(skill.get('Proficiency_Level', 0), is_leadership=is_leadership)
    
    style_name = ParagraphStyle('SName', fontName='Helvetica-Bold', fontSize=9, leading=11, spaceAfter=2)
    style_def = ParagraphStyle('SDef', fontName='Helvetica', fontSize=8, textColor=colors.HexColor('#4b5563'), leading=10)
    
    name = Paragraph(skill.get('Skill_Name', ''), style_name)
    defn = Paragraph(skill.get('Skill_Definition', ''), style_def)
    
    # Optimization: Just stack them vertically
    # [Dots]
    # [Name]
    # [Def]
    
    return [
        dots,
        Spacer(1, 2),
        name,
        Spacer(1, 2),
        defn
    ]


def create_skills_matrix_pdf(data: List[Dict], filters: Dict) -> BytesIO:
    buffer = BytesIO()
    
    # Page setup
    doc = SimpleDocTemplate(
        buffer,
        pagesize=landscape(A4),
        rightMargin=10*mm,
        leftMargin=10*mm,
        topMargin=20*mm,
        bottomMargin=15*mm
    )
    
    elements = []
    
    # Constants for layout
    col_width_band = 25*mm
    # A4 Landscape width ~297mm - 20mm margin = 277mm
    # Remaining for columns: 277 - 25 = 252mm -> 126mm each
    col_width_content = 126*mm 
    
    styles = getSampleStyleSheet()
    style_band_title = ParagraphStyle('BandTitle', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=14, textColor=COLOR_BAND_TEXT, alignment=TA_CENTER)
    
    # White Label for Header
    style_header_label = ParagraphStyle('HeaderLabel', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=9, textColor=colors.white, alignment=TA_CENTER)

    
    # Filter Summary
    if any(filters.values()):
        filter_text = []
        for k, v in filters.items():
            if v:
                val = ", ".join(v) if isinstance(v, list) else str(v)
                filter_text.append(f"<b>{k}:</b> {val}")
        
        if filter_text:
            elements.append(Paragraph(" | ".join(filter_text), ParagraphStyle('Filters', fontSize=8, textColor=colors.gray)))
            elements.append(Spacer(1, 5))

    # Main Table Data list
    table_data = []
    
    # Header Row
    header_row = [
        Paragraph("<b>BAND</b>", style_header_label),
        Paragraph("<b>FUNCTIONAL SKILLS</b>", style_header_label),
        Paragraph("<b>LEADERSHIP SKILLS</b>", style_header_label)
    ]
    table_data.append(header_row)
    
    # Group Data
    grouped = {}
    band_order = get_band_order()
    
    for item in data:
        band = item.get('Band', 'Unassigned')
        if band not in grouped:
            grouped[band] = {'functional': [], 'leadership': []}
            
        ctype = item.get('Competency_Type', '')
        if ctype == 'Behavioral' or ctype == 'Raymond Leadership Competency':
            grouped[band]['leadership'].append(item)
        else:
            grouped[band]['functional'].append(item)

    sorted_bands = sorted(grouped.keys(), key=lambda x: band_order.index(x) if x in band_order else 999)

    # Styles list for the main table
    # Row 0 is Header -> Red Background
    table_styles = [
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#e5e7eb')),
        ('BACKGROUND', (0,0), (-1,0), HEADER_RED), # Red Header
        ('ALIGN', (0,0), (-1,0), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('LEFTPADDING', (0,0), (-1,-1), 4),
        ('RIGHTPADDING', (0,0), (-1,-1), 4),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
    ]

    current_row_idx = 1 # Start after header

    for band in sorted_bands:
        content = grouped[band]
        func_list = content['functional']
        lead_list = content['leadership']
        
        # Determine number of rows needed for this band
        num_rows = max(len(func_list), len(lead_list))
        if num_rows == 0:
            continue
        
        for i in range(num_rows):
            row_content = []
            
            # Column 1: Band Label
            if i == 0:
                band_cell = [
                    Spacer(1, 10),
                    Paragraph(band, style_band_title),
                    # Removed redundant "BAND" label as requested
                ]
            else:
                band_cell = "" 
                
            row_content.append(band_cell)
            
            # Column 2: Functional Skill
            if i < len(func_list):
                skill = func_list[i]
                skill_content = create_skill_cell_content(skill, False, col_width_content)
            else:
                skill_content = ""
            row_content.append(skill_content)
                
            # Column 3: Leadership Skill
            if i < len(lead_list):
                skill = lead_list[i]
                skill_content = create_skill_cell_content(skill, True, col_width_content)
            else:
                skill_content = ""
            row_content.append(skill_content)

            table_data.append(row_content)
            
            # Styles specific to this row
            
            # Functional Col (1)
            if i < len(func_list):
                table_styles.append(('BACKGROUND', (1, current_row_idx), (1, current_row_idx), COLOR_FUNC_BG))
                table_styles.append(('BOX', (1, current_row_idx), (1, current_row_idx), 0.5, COLOR_FUNC_BORDER))

            # Leadership Col (2)
            if i < len(lead_list):
                table_styles.append(('BACKGROUND', (2, current_row_idx), (2, current_row_idx), COLOR_LEAD_BG))
                table_styles.append(('BOX', (2, current_row_idx), (2, current_row_idx), 0.5, COLOR_LEAD_BORDER))
            
            # Band Col (0) Background - uniform
            table_styles.append(('BACKGROUND', (0, current_row_idx), (0, current_row_idx), COLOR_BAND_BG))
            
            current_row_idx += 1

        # Border separator
        start_row = current_row_idx - num_rows
        table_styles.append(('LINEABOVE', (0, start_row), (-1, start_row), 1.5, colors.HexColor('#1e40af')))

    # Create the Main Table
    main_table = Table(
        table_data,
        colWidths=[col_width_band, col_width_content, col_width_content],
        style=TableStyle(table_styles),
        repeatRows=1 # Repeat header
    )
    
    elements.append(main_table)

    try:
        doc.build(elements, onFirstPage=create_header_footer, onLaterPages=create_header_footer)
    except Exception as e:
        logger.error(f"Error building PDF: {e}")
        doc.build(elements)
    
    buffer.seek(0)
    return buffer


@router.post("/export-pdf")
async def export_skills_matrix_pdf(request_data: Dict[str, Any]):
    try:
        data = request_data.get('data', [])
        filters = request_data.get('filters', {})
        
        if not data:
            raise HTTPException(status_code=400, detail="No data provided")
        
        pdf_buffer = create_skills_matrix_pdf(data, filters)
        filename = f"skills_matrix_full_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        
        return StreamingResponse(
            pdf_buffer,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename={filename}"
            }
        )
    except Exception as e:
        logger.error(f"PDF generation failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"PDF generation failed: {str(e)}")
