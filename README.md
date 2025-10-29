# Price Ticket Generator

A Python web application for generating professional price tickets as PDF files. Select products from a database or add custom one-time tickets.

## Features

- **Modern UI**: Clean, gradient-based design inspired by contemporary web apps
- **Product Database**: Read-only JSON database of products with quick codes, names, and RRP
- **Custom Tickets**: Add temporary custom tickets without modifying the database
- **Interactive Selection**: Visual card-based product selection with instant feedback
- **PDF Generation**: Professional price tickets in a clean, printable layout
- **Session-Based**: Custom tickets are stored in session and cleared after PDF generation

## Installation

1. **Navigate to the repository:**
   ```bash
   cd /workspaces/rubi_price-ticket_generator
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

## Usage

1. **Start the application:**
   ```bash
   python app.py
   ```

2. **Access the web interface:**
   Open your browser and navigate to `http://localhost:5000`

3. **Generate tickets:**
   - Browse the product database displayed as cards
   - Click on products to select them (or use Select All/Deselect All)
   - Optionally add custom tickets for one-time use
   - Click "Generate PDF Tickets" to create and download your tickets
   - Custom tickets are automatically cleared after generation

## Product Database

Products are stored in `products.json` as a **read-only database**. The web interface does not allow permanent additions or modifications. To update the product database, edit the JSON file directly:

```json
[
  {
    "id": 1,
    "quick_code": "ABC123",
    "name": "Product Name",
    "rrp": 99.99
  }
]
```


## Project Structure

```
rubi_price-ticket_generator/
├── app.py                  # Main Flask application
├── pdf_generator.py        # PDF generation logic using ReportLab
├── products.json           # Product database (read-only via web interface)
├── requirements.txt        # Python dependencies
├── templates/              # HTML templates
│   ├── base.html          # Base template with navigation
│   └── index.html         # Main page with product selection
├── static/                 # CSS and static files
│   └── style.css          # Modern gradient-based styling
└── generated_tickets/      # Output directory for PDFs (auto-created)
```

## Customization

### Update Product Database
Edit `products.json` directly to add, modify, or remove products:
- Each product needs: `id` (unique number), `quick_code`, `name`, `rrp`

### Modify Ticket Design
Edit `pdf_generator.py` to change:
- Ticket dimensions (default: 90mm × 65mm)
- Layout (default: 2 columns × 4 rows = 8 tickets per page)
- Fonts, colors, and border styles
- Price display formatting

### Customize Styling
Edit `static/style.css` to adjust:
- Color gradients (currently purple/blue theme)
- Card layouts and hover effects
- Button styles and spacing
- Responsive breakpoints

## Technical Details

- **Backend**: Flask (Python web framework)
- **PDF Generation**: ReportLab library
- **Data Storage**: JSON file for products, session storage for custom tickets
- **Styling**: Pure CSS with modern gradient design
- **Page Size**: A4 with 2×4 ticket grid

## License

MIT License - Feel free to use and modify for your needs.