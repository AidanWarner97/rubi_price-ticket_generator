from flask import Flask, render_template, request, redirect, url_for, send_file, flash, session
import json
import os
from datetime import datetime
from pdf_generator import generate_price_tickets

app = Flask(__name__)
app.secret_key = 'your-secret-key-change-in-production'

# Data file path
DATA_FILE = 'products.json'
OUTPUT_DIR = 'generated_tickets'

# Ensure output directory exists
os.makedirs(OUTPUT_DIR, exist_ok=True)


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
    return render_template('index.html', products=products, custom_tickets=custom_tickets)


@app.route('/add_custom', methods=['POST'])
def add_custom_ticket():
    """Add a custom ticket temporarily (not saved to database)"""
    custom_tickets = session.get('custom_tickets', [])
    
    new_ticket = {
        'id': f"custom_{len(custom_tickets) + 1}",
        'quick_code': request.form['quick_code'],
        'name': request.form['name'],
        'rrp': float(request.form['rrp']),
        'is_custom': True
    }
    
    custom_tickets.append(new_ticket)
    session['custom_tickets'] = custom_tickets
    session.modified = True
    
    flash('Custom ticket added!', 'success')
    return redirect(url_for('index'))


@app.route('/remove_custom/<ticket_id>', methods=['POST'])
def remove_custom_ticket(ticket_id):
    """Remove a custom ticket from session"""
    custom_tickets = session.get('custom_tickets', [])
    custom_tickets = [t for t in custom_tickets if t['id'] != ticket_id]
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
    app.run(debug=True, host='0.0.0.0', port=5000)
