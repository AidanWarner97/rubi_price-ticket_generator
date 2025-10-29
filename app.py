from flask import Flask, render_template, request, redirect, url_for, send_file, flash, session
import json
import os
from datetime import datetime
from pdf_generator import generate_price_tickets

app = Flask(__name__)
app.secret_key = 'your-secret-key-change-in-production'

# Base URL for deployment under subpath
BASE_URL = '/rubi-price-ticket'

# Data file path
DATA_FILE = 'products.json'
OUTPUT_DIR = 'generated_tickets'

# Ensure output directory exists
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Context processor to inject base_url into all templates
@app.context_processor
def inject_base_url():
    return {'base_url': BASE_URL}

# Custom static file route to handle subpath deployment
@app.route('/static/<path:filename>')
def static_files(filename):
    """Serve static files with the correct subpath"""
    print(f"Serving static file: {filename}")
    return app.send_static_file(filename)

# Test route to debug
@app.route('/test')
def test_route():
    return "Flask app is working at subpath!"

# Also handle static files without the subpath (fallback)
@app.route('/static/<path:filename>')
def static_fallback(filename):
    """Fallback static file serving"""
    print(f"Serving static file via fallback: {filename}")
    return app.send_static_file(filename)

# CSS route as a workaround for static file issues
@app.route('/static/style.css')
def serve_css():
    """Serve CSS directly to bypass static file issues"""
    try:
        with open(os.path.join(app.static_folder, 'style.css'), 'r') as f:
            css_content = f.read()
        return css_content, 200, {'Content-Type': 'text/css'}
    except FileNotFoundError:
        return "/* CSS file not found */", 404, {'Content-Type': 'text/css'}


def load_products():
    """Load products from JSON file (read-only)"""
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as f:
            return json.load(f)
    return []


@app.route('/')
def index():
    """Main page - Display products for selection and allow custom tickets"""
    products = load_products()
    # Get custom tickets from session
    custom_tickets = session.get('custom_tickets', [])
    print(f"Base URL: {BASE_URL}")
    print(f"Static URL would be: {BASE_URL}/static/style.css")
    return render_template('index.html', products=products, custom_tickets=custom_tickets)


@app.route('/add_custom', methods=['POST'])
def add_custom_ticket():
    """Add a custom ticket temporarily (not saved to database)"""
    custom_tickets = session.get('custom_tickets', [])
    # Basic server-side validation and parsing
    quick_code = request.form.get('quick_code', '').strip()
    name = request.form.get('name', '').strip()
    rrp_raw = request.form.get('rrp', '').strip()

    # Helper to parse currency-like input (accepts '£', '$', commas, spaces)
    def parse_rrp(value: str):
        if not value:
            raise ValueError('RRP is required')
        # Remove common currency symbols and separators
        cleaned = value.replace('£', '').replace('$', '').replace(',', '').strip()
        if cleaned == '':
            raise ValueError('RRP is required')
        return float(cleaned)

    # Validate fields
    if not quick_code:
        flash('Quick code is required for a custom ticket.', 'error')
        return redirect(url_for('index'))

    if not name:
        flash('Product name is required for a custom ticket.', 'error')
        return redirect(url_for('index'))

    try:
        rrp = parse_rrp(rrp_raw)
    except ValueError as e:
        flash(f'Invalid RRP value: {str(e)}', 'error')
        return redirect(url_for('index'))

    # Generate unique ID based on timestamp to avoid duplicates
    import time
    new_ticket = {
        'id': f"custom_{int(time.time() * 1000)}",  # Use timestamp in milliseconds for uniqueness
        'quick_code': quick_code,
        'name': name,
        'rrp': rrp,
        'is_custom': True
    }

    custom_tickets.append(new_ticket)
    session['custom_tickets'] = custom_tickets
    session.modified = True
    
    flash('Custom ticket added!', 'success')
    return redirect(url_for('index'))


@app.route('/remove_custom/<ticket_id>', methods=['POST'])
@app.route('/remove_custom', methods=['POST'])
def remove_custom_ticket(ticket_id=None):
    """Remove a custom ticket from session"""
    # Get ticket_id from URL parameter or form data
    if ticket_id is None:
        ticket_id = request.form.get('ticket_id')
    
    if not ticket_id:
        flash('No ticket ID provided for removal.', 'error')
        return redirect(url_for('index'))
    
    custom_tickets = session.get('custom_tickets', [])
    original_count = len(custom_tickets)
    
    # Debug: Print ticket IDs for debugging
    print(f"Attempting to remove ticket_id: {ticket_id}")
    print(f"Current ticket IDs: {[t['id'] for t in custom_tickets]}")
    
    custom_tickets = [t for t in custom_tickets if t['id'] != ticket_id]
    
    if len(custom_tickets) == original_count:
        flash(f'Custom ticket with ID {ticket_id} not found.', 'error')
    else:
        session['custom_tickets'] = custom_tickets
        session.modified = True
        flash('Custom ticket removed!', 'success')
    
    return redirect(url_for('index'))


@app.route('/generate', methods=['POST'])
def generate_tickets():
    """Generate PDF tickets for selected products and custom tickets"""
    products = load_products()
    custom_tickets = session.get('custom_tickets', [])
    
    selected_ids = request.form.getlist('product_ids[]')
    
    if not selected_ids and not custom_tickets:
        flash('Please select at least one product or add a custom ticket!', 'error')
        return redirect(url_for('index'))
    
    # Filter selected products from database
    selected_products = [p for p in products if str(p['id']) in selected_ids]
    
    # Combine with custom tickets
    all_tickets = selected_products + custom_tickets
    
    if not all_tickets:
        flash('Please select at least one product or add a custom ticket!', 'error')
        return redirect(url_for('index'))
    
    # Generate PDF
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_file = os.path.join(OUTPUT_DIR, f'price_tickets_{timestamp}.pdf')
    
    try:
        generate_price_tickets(all_tickets, output_file)
        # Clear custom tickets after successful generation
        session['custom_tickets'] = []
        session.modified = True
        flash(f'Successfully generated tickets for {len(all_tickets)} products!', 'success')
        return send_file(output_file, as_attachment=True, download_name=f'price_tickets_{timestamp}.pdf')
    except Exception as e:
        flash(f'Error generating PDF: {str(e)}', 'error')
        return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5002)
