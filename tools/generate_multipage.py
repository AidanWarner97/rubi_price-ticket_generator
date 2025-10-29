import json
import sys
from pathlib import Path

# Ensure repo root is on sys.path so imports work when running from tools/
BASE = Path('/workspaces/rubi_price-ticket_generator')
sys.path.insert(0, str(BASE))

from pdf_generator import generate_price_tickets

with open(BASE / 'products.json', 'r') as f:
    base = json.load(f)

# Build ~60 sample products by cycling the base list and varying quick_code/name/rrp
products = []
for i in range(60):
    src = base[i % len(base)].copy()
    src['quick_code'] = f"QC{i+1:03d}"
    # Make some names longer so we exercise wrapping
    if i % 7 == 0:
        src['name'] = src['name'] + ' — Very Long Product Name That Wraps' * ((i % 3) + 1)
    else:
        src['name'] = src['name']
    # rrp in product data should be a numeric value (float) — pdf generator formats it
    src['rrp'] = round(9.99 + (i % 100), 2)
    products.append(src)

out_dir = BASE / 'generated_tickets'
out_dir.mkdir(parents=True, exist_ok=True)
output_file = out_dir / 'multipage_test.pdf'

print(f"Generating {output_file} with {len(products)} tickets...")
generate_price_tickets(products, str(output_file))
print('Done.')
