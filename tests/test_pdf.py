from src.engine import PDFGenerator
from src.schema import Customer, LineItem, Invoice
import os


def test_pdf_generator_creation():
    generator = PDFGenerator()
    assert generator.renderer is not None


def test_generate_pdf_full_pipeline():
    # Create sample data
    customer = Customer(name="Alice Smith", address="789 Oak Ave\nSpringfield, IL 62701")
    line_items = [
        LineItem(description="Service Fee", quantity=1, unit_price=100.00),
        LineItem(description="Consulting", quantity=5, unit_price=50.00)
    ]
    invoice = Invoice(
        invoice_number="INV-003",
        date="2023-10-03",
        customer=customer,
        line_items=line_items
    )

    # Generate PDF
    generator = PDFGenerator()
    pdf_bytes = generator.generate_pdf(
        "invoice.html",
        invoice,
        page_size='a4',
        margins='15mm',
        orientation='portrait',
        title='Invoice INV-003',
        author='DocGen'
    )

    # Verify PDF bytes
    assert isinstance(pdf_bytes, bytes)
    assert len(pdf_bytes) > 0  # Should have content

    # Save to file
    output_dir = "output"
    os.makedirs(output_dir, exist_ok=True)
    pdf_path = os.path.join(output_dir, "sample_invoice.pdf")
    with open(pdf_path, 'wb') as f:
        f.write(pdf_bytes)

    # Verify file
    assert os.path.exists(pdf_path)
    assert os.path.getsize(pdf_path) > 0

    print(f"PDF generated and saved to {pdf_path}")
    print(f"PDF size: {len(pdf_bytes)} bytes")


def test_generate_pdf_with_options():
    # Test with different options
    customer = Customer(name="Bob Johnson", address="321 Pine St")
    invoice = Invoice(
        invoice_number="INV-004",
        date="2023-10-04",
        customer=customer,
        line_items=[LineItem(description="Product", quantity=1, unit_price=75.00)]
    )

    generator = PDFGenerator()
    pdf_bytes = generator.generate_pdf(
        "invoice.html",
        invoice,
        page_size='letter',
        margins='20mm 25mm',
        orientation='landscape',
        title='Test Invoice',
        author='Test Author'
    )

    assert len(pdf_bytes) > 0

    # Save with different name
    pdf_path = "output/test_options.pdf"
    with open(pdf_path, 'wb') as f:
        f.write(pdf_bytes)

    assert os.path.exists(pdf_path)


if __name__ == "__main__":
    test_generate_pdf_full_pipeline()
    test_generate_pdf_with_options()
    print("PDF tests passed!")