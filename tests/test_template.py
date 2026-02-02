from jinja2 import Environment, FileSystemLoader
from src.schema import Customer, LineItem, Invoice

# Create sample data
customer = Customer(name="John Doe", address="123 Main St, Anytown, USA")
line_items = [
    LineItem(description="Widget A", quantity=2, unit_price=15.50),
    LineItem(description="Widget B", quantity=1, unit_price=25.00),
    LineItem(description="Widget C", quantity=3, unit_price=10.75)
]
invoice = Invoice(
    invoice_number="INV-001",
    date="2023-10-01",
    customer=customer,
    line_items=line_items
)

# Set up Jinja2 environment
env = Environment(loader=FileSystemLoader('src/templates'))
template = env.get_template('invoice.html')

# Render the template
html_output = template.render(invoice=invoice)

# Print a portion of the HTML to verify
print("Rendered HTML (first 500 characters):")
print(html_output[:500])
print("...")

# To verify total
print(f"\nInvoice Total: ${invoice.total_amount:.2f}")
assert invoice.total_amount == 2*15.50 + 1*25.00 + 3*10.75  # Should be 82.25

print("Template rendering test passed!")