from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, mm
from reportlab.platypus import (
    SimpleDocTemplate, Table, TableStyle, Paragraph, 
    Spacer, PageBreak, Image as RLImage, KeepTogether
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from io import BytesIO
from datetime import datetime
from typing import List, Dict, Any
import logging

router = APIRouter()
logger = logging.getLogger(__name__)


def get_band_order():
    return ['Band 1A', 'Band 1B', 'Band 2A', 'Band 2B', 'Band 3', 'Band 4', 'Band 5']


def create_header_footer(canvas, doc):
    """Add header and footer to each page"""
    canvas.saveState()
    width, height = A4
    
    # Header
    canvas.setFont('Helvetica-Bold', 12)
    canvas.setFillColor(colors.HexColor('#CD202C'))  # Raymond Red
    canvas.drawString(20*mm, height - 15*mm, "Manpower & Skills Matrix Report")
    
    canvas.setFont('Helvetica', 8)
    canvas.setFillColor(colors.black)
    canvas.drawRightString(width - 20*mm, height - 15*mm, 
                          f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    
    # Footer
    canvas.setFont('Helvetica', 8)
    canvas.drawCentredString(width/2, 10*mm, f"Page {doc.page}")
    
    canvas.restoreState()


def create_skills_matrix_pdf(data: List[Dict], filters: Dict) -> BytesIO:
    """
    Generate a visual PDF matching the Skills Matrix Dashboard style
    Grouping by Band -> Functional/Leadership
    """
    buffer = BytesIO()
    
    # Use landscape orientation
    doc = SimpleDocTemplate(
        buffer,
        pagesize=landscape(A4),
        rightMargin=15*mm,
        leftMargin=15*mm,
        topMargin=20*mm,
        bottomMargin=20*mm
    )
    
    elements = []
    styles = getSampleStyleSheet()
    
    # Custom visuals matching dashboard
    # Functional: Emerald Green (#10b981 / #059669)
    # Leadership: Purple (#8b5cf6 / #7c3aed)
    
    functional_color = colors.HexColor('#059669')
    leadership_color = colors.HexColor('#7c3aed')
    band_header_bg = colors.HexColor('#1e40af') # Blue for Band Header
    
    # Styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=20,
        textColor=colors.HexColor('#CD202C'),
        spaceAfter=12,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )
    
    filter_style = ParagraphStyle(
        'FilterStyle',
        parent=styles['Normal'],
        fontSize=9,
        textColor=colors.HexColor('#4b5563'),
        spaceAfter=8
    )

    band_header_style = ParagraphStyle(
        'BandHeader',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=colors.white,
        backColor=band_header_bg,
        borderPadding=6,
        spaceAfter=6,
        fontName='Helvetica-Bold'
    )
    
    sub_header_style = ParagraphStyle(
        'SubHeader',
        parent=styles['Heading3'],
        fontSize=11,
        textColor=colors.black,
        spaceAfter=4,
        fontName='Helvetica-Bold'
    )

    # 1. Title
    elements.append(Paragraph("Manpower & Skills Matrix", title_style))
    elements.append(Spacer(1, 10))
    
    # 2. Filters
    if any(filters.values()):
        filter_text = "<b>Filters Applied:</b> "
        f_list = []
        for k, v in filters.items():
            if v:
                val = ", ".join(v) if isinstance(v, list) else str(v)
                f_list.append(f"{k}: {val}")
        filter_text += " | ".join(f_list)
        elements.append(Paragraph(filter_text, filter_style))
        elements.append(Spacer(1, 15))
    
    # 3. Group Data by Band
    grouped_data = {}
    band_order = get_band_order()
    
    for item in data:
        band = item.get('Band', 'Unassigned')
        if band not in grouped_data:
            grouped_data[band] = {'functional': [], 'leadership': []}
            
        ctype = item.get('Competency_Type', '')
        # Logic from SkillsMatrix.jsx
        if ctype == 'Behavioral' or ctype == 'Raymond Leadership Competency':
            grouped_data[band]['leadership'].append(item)
        else:
            grouped_data[band]['functional'].append(item)

    # Sort Bands
    sorted_bands = sorted(grouped_data.keys(), key=lambda x: band_order.index(x) if x in band_order else 999)

    # 4. Generate Sections
    for band in sorted_bands:
        band_content = grouped_data[band]
        if not band_content['functional'] and not band_content['leadership']:
            continue
            
        # Band Header
        elements.append(KeepTogether([
            Paragraph(f"{band}", band_header_style),
            Spacer(1, 5)
        ]))

        # Helper to create table for a skill type
        def create_skill_table(skills, is_leadership):
            if not skills:
                return None
                
            color_accent = leadership_color if is_leadership else functional_color
            bg_accent = colors.HexColor('#f3e8ff') if is_leadership else colors.HexColor('#ecfdf5') # Light purple/emerald
            
            # Header Row
            headers = [
                Paragraph('<b>Skill Name</b>', styles['Normal']),
                Paragraph('<b>Proficiency</b>', styles['Normal']),
                Paragraph('<b>Role / Function</b>', styles['Normal']),
                Paragraph('<b>Definition</b>', styles['Normal'])
            ]
            
            data_rows = [headers]
            
            for skill in skills:
                name = skill.get('Skill_Name', '')
                prof = str(skill.get('Proficiency_Level', 0))
                role = skill.get('Job_Role_Name_without_concat', '') or skill.get('Function', '')
                defn = skill.get('Skill_Definition', '')[:100] + '...' if len(skill.get('Skill_Definition', '')) > 100 else skill.get('Skill_Definition', '')
                
                # Style Proficiency Badge (Simulated with text color/bold)
                prof_para = Paragraph(f"<font color='{color_accent.hexval()}'><b>{prof}</b></font>", styles['Normal'])
                
                row = [
                    Paragraph(f"<b>{name}</b>", styles['Normal']),
                    prof_para,
                    Paragraph(role, styles['Normal']),
                    Paragraph(f"<font size=7 color='#666666'>{defn}</font>", styles['Normal'])
                ]
                data_rows.append(row)
                
            # Table Layout
            # Widths: Name(25%), Prof(10%), Role(25%), Defr(40%)
            available_width = landscape(A4)[0] - 30*mm
            col_widths = [available_width * 0.25, available_width * 0.10, available_width * 0.25, available_width * 0.40]
            
            t = Table(data_rows, colWidths=col_widths, repeatRows=1)
            
            t.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), color_accent),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('ALIGN', (0, 0), (-1, 0), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
                ('TOPPADDING', (0, 0), (-1, 0), 8),
                
                ('BACKGROUND', (0, 1), (-1, -1), bg_accent),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.white),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ]))
            
            return t

        # Functional Section
        if band_content['functional']:
            elements.append(Paragraph("Functional Skills", sub_header_style))
            t_func = create_skill_table(band_content['functional'], is_leadership=False)
            if t_func:
                elements.append(t_func)
            elements.append(Spacer(1, 10))

        # Leadership Section
        if band_content['leadership']:
            elements.append(Paragraph("Leadership Skills", sub_header_style))
            t_lead = create_skill_table(band_content['leadership'], is_leadership=True)
            if t_lead:
                elements.append(t_lead)
            elements.append(Spacer(1, 15))
            
        elements.append(Spacer(1, 10))
        # Page Break after each band? Or continuous? Continuous is better for flow, unless huge.
        # Let's add a line separator
        # elements.append(Paragraph("<hr/>", styles['Normal'])) 

    try:
        doc.build(elements, onFirstPage=create_header_footer, onLaterPages=create_header_footer)
    except Exception as e:
        logger.error(f"Error building PDF: {e}")
        doc.build(elements)
    
    buffer.seek(0)
    return buffer


@router.post("/export-pdf")
async def export_skills_matrix_pdf(request_data: Dict[str, Any]):
    """
    Export visual skills matrix PDF
    """
    try:
        data = request_data.get('data', [])
        filters = request_data.get('filters', {})
        
        if not data:
            raise HTTPException(status_code=400, detail="No data provided")
        
        pdf_buffer = create_skills_matrix_pdf(data, filters)
        
        filename = f"skills_matrix_visual_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        
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
