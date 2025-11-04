from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.units import inch, mm, cm
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.pdfbase import pdfmetrics
import os


def generate_price_tickets(products, output_file, debug=False):
    """
    Generate a PDF with price tickets for selected products.
    Each ticket shows: Rubi Logo, Quick Code, Product Name, and RRP
    Ticket dimensions: 6.09cm wide x 3.49cm tall
    """
    # Page setup - using A4 landscape to fit larger tickets
    page_width, page_height = A4
    # Swap for landscape
    page_width, page_height = page_height, page_width
    
    c = canvas.Canvas(output_file, pagesize=(page_width, page_height))
    
    # Ticket dimensions (as specified: 6.09cm x 3.49cm)
    ticket_width = 6.09 * cm
    ticket_height = 3.49 * cm
    margin = 10 * mm
    
    # Calculate how many tickets fit per page
    cols = int((page_width - 2 * margin) / (ticket_width + 5 * mm))
    rows = int((page_height - 2 * margin) / (ticket_height + 5 * mm))
    tickets_per_page = cols * rows
    
    # Calculate positions with spacing
    # If available spacing is negative (too many columns/rows), clamp to 0 so tickets keep their specified size
    x_spacing = (page_width - 2 * margin - (cols * ticket_width)) / (cols - 1) if cols > 1 else 0
    y_spacing = (page_height - 2 * margin - (rows * ticket_height)) / (rows - 1) if rows > 1 else 0
    x_spacing = max(0, x_spacing)
    y_spacing = max(0, y_spacing)

    # Debug printouts to help verify sizes (in points and cm)
    if debug:
        print("PAGE (points):", page_width, "x", page_height)
        print("PAGE (cm):", page_width / cm, "x", page_height / cm)
        print("MARGIN (mm):", margin / mm)
        print("TICKET (points):", ticket_width, "x", ticket_height)
        print("TICKET (cm):", ticket_width / cm, "x", ticket_height / cm)
        print("COLS x ROWS:", cols, "x", rows, "=> tickets_per_page:", tickets_per_page)
        print("x_spacing (points/mm):", x_spacing, "/", x_spacing / mm)
        print("y_spacing (points/mm):", y_spacing, "/", y_spacing / mm)
    
    ticket_count = 0
    
    for product in products:
        # Calculate position
        page_position = ticket_count % tickets_per_page
        col = page_position % cols
        row = page_position // cols
        
        x = margin + col * (ticket_width + x_spacing)
        y = page_height - margin - (row + 1) * ticket_height - row * y_spacing
        
        # Draw ticket
        draw_ticket(c, x, y, ticket_width, ticket_height, product)
        
        ticket_count += 1
        
        # New page if needed
        if ticket_count % tickets_per_page == 0 and ticket_count < len(products):
            c.showPage()
    
    c.save()


def draw_ticket(c, x, y, width, height, product):
    """Draw a single price ticket matching the Rubi design"""
    # Draw outer border (black, 1pt)
    c.setStrokeColor(colors.black)
    c.setLineWidth(1)
    c.rect(x, y, width, height)
    
    # Logo section on the left (approximately 1/3 of width)
    logo_width = width * 0.35
    
    # Vertical divider line after logo
    c.setLineWidth(1)
    c.line(x + logo_width, y, x + logo_width, y + height)
    
    # Draw Rubi logo in the left section
    logo_path = 'rubi.png'
    if os.path.exists(logo_path):
        # Calculate logo dimensions to fit with minimal padding - make it bigger
        logo_padding = 0.5 * mm
        available_width = logo_width - (2 * logo_padding)
        available_height = height - (2 * logo_padding)
        
        # Center the logo
        logo_x = x + logo_padding
        logo_y = y + logo_padding
        
        try:
            c.drawImage(logo_path, logo_x, logo_y, 
                       width=available_width, 
                       height=available_height,
                       preserveAspectRatio=True, 
                       mask='auto')
        except:
            # Fallback to text if image fails
            c.setFillColor(colors.black)
            c.setFont("Helvetica-Bold", 12)
            rubi_text = "RUBI"
            text_width = c.stringWidth(rubi_text, "Helvetica-Bold", 12)
            c.drawString(x + (logo_width - text_width) / 2, y + height / 2 - 4, rubi_text)
    else:
        # Fallback to text if logo file not found
        c.setFillColor(colors.black)
        c.setFont("Helvetica-Bold", 12)
        rubi_text = "RUBI"
        text_width = c.stringWidth(rubi_text, "Helvetica-Bold", 12)
        c.drawString(x + (logo_width - text_width) / 2, y + height / 2 - 4, rubi_text)
    
    # Right section with product details
    right_x = x + logo_width + 1.5 * mm  # Reduced left padding
    right_width = width - logo_width - 3 * mm
    
    # Horizontal divider lines in right section with exact heights
    # Top section for QC code - 1.06cm
    qc_section_height = 1.06 * cm
    # Middle section for product name - 1.63cm
    name_section_height = 1.63 * cm
    # Bottom section for RRP - remaining height
    rrp_section_height = height - qc_section_height - name_section_height
    
    # Draw horizontal dividers
    c.setLineWidth(1)
    c.line(x + logo_width, y + height - qc_section_height, x + width, y + height - qc_section_height)
    c.line(x + logo_width, y + rrp_section_height, x + width, y + rrp_section_height)
    
    # QC Code (top right section) - vertically centered, two lines (QC and RU)
    # Use font metrics (points) so units are consistent with canvas coordinates
    font_name_qc = "Helvetica"
    font_size_qc = 11
    c.setFont(font_name_qc, font_size_qc)
    c.setFillColor(colors.black)

    # Get ascent/descent in points and compute line height + leading
    ascent_qc = pdfmetrics.getAscent(font_name_qc, font_size_qc)
    descent_qc = abs(pdfmetrics.getDescent(font_name_qc, font_size_qc))
    line_height_qc = ascent_qc + descent_qc
    leading_qc = font_size_qc * 0.2

    # Two-line block total height
    total_block_height = 2 * line_height_qc + leading_qc

    # QC section top and bottom in canvas coordinates
    qc_section_top = y + height
    qc_section_bottom = qc_section_top - qc_section_height

    # Vertical space to leave above the text block to vertically center it
    space_top = (qc_section_height - total_block_height) / 2.0

    # Baseline for first line: top_of_block = baseline + ascent => baseline = top_of_block - ascent
    top_of_block = qc_section_top - space_top
    first_baseline = top_of_block - ascent_qc

    # Draw QC then RU on the next baseline down
    c.drawString(right_x, first_baseline, f"QC: {product.get('quick_code', '')}")
    second_baseline = first_baseline - (line_height_qc + leading_qc)
    c.drawString(right_x, second_baseline, f"RU: {product.get('rubi_code', '')}")
    
    # Product Name (middle right section) - vertically centered, size 11, NOT BOLD
    font_name = "Helvetica"
    font_size = 11
    c.setFont(font_name, font_size)

    # Wrap product name if too long
    name_lines = wrap_text(product['name'], right_width - 2 * mm, c, font_name, font_size)

    # Use font metrics for vertical centering (works for 1 or 2 lines)
    ascent = pdfmetrics.getAscent(font_name, font_size)
    descent = abs(pdfmetrics.getDescent(font_name, font_size))
    line_height = ascent + descent
    leading = font_size * 0.2

    num_lines = min(len(name_lines), 2)
    total_text_height = num_lines * line_height + (num_lines - 1) * leading

    # Name section top and bottom in points
    section_bottom = y + rrp_section_height
    section_top = section_bottom + name_section_height

    # Space to leave above the text block to vertically center it
    space_top = (name_section_height - total_text_height) / 2.0

    # Baseline for first line: top_of_block = baseline + ascent => baseline = top_of_block - ascent
    top_of_block = section_top - space_top
    first_baseline = top_of_block - ascent

    # Draw each line at its baseline, preserving the leading gap
    for i, line in enumerate(name_lines[:num_lines]):
        baseline = first_baseline - i * (line_height + leading)
        c.drawString(right_x, baseline, line)
    
    # RRP (bottom right section) - vertically centered, size 11, NOT BOLD
    c.setFont("Helvetica", 11)
    c.setFillColor(colors.black)
    
    # Build the full RRP text on one line
    rrp_text = f"RRP: £{product['rrp']:.2f}"
    
    # Calculate vertical center of RRP section (remaining height)
    rrp_text_height = 11 * 0.352778  # Approximate height in mm for font size 11
    rrp_y = y + rrp_section_height / 2 - rrp_text_height / 2
    
    c.drawString(right_x, rrp_y, rrp_text)
    
    c.setFillColor(colors.black)


def wrap_text(text, max_width, canvas_obj, font_name, font_size):
    """Simple text wrapping function"""
    words = text.split()
    lines = []
    current_line = []
    
    for word in words:
        test_line = ' '.join(current_line + [word])
        width = canvas_obj.stringWidth(test_line, font_name, font_size)
        
        if width <= max_width:
            current_line.append(word)
        else:
            if current_line:
                lines.append(' '.join(current_line))
            current_line = [word]
    
    if current_line:
        lines.append(' '.join(current_line))
    
    return lines
