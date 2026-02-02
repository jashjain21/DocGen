from src.storage import FileManager
from src.engine import PDFGenerator
from src.schema import Customer, LineItem, Invoice
import os
import shutil


def test_file_manager_creation():
    manager = FileManager("test_output")
    assert os.path.exists("test_output")
    assert os.path.exists(os.path.join("test_output", "manifest.json"))
    shutil.rmtree("test_output")  # Cleanup


def test_save_pdf_and_manifest():
    manager = FileManager("test_output")
    # Generate sample PDF
    generator = PDFGenerator()
    customer = Customer(name="Test User", address="Test Address")
    invoice = Invoice(
        invoice_number="TEST-001",
        date="2023-10-01",
        customer=customer,
        line_items=[LineItem(description="Test Item", quantity=1, unit_price=10.00)]
    )
    pdf_bytes = generator.generate_pdf("invoice.html", invoice, title="Test Invoice")

    # Save PDF
    path = manager.save_pdf(pdf_bytes, "test_invoice.pdf", {'invoice_number': 'TEST-001', 'customer': 'Test User'})
    assert os.path.exists(path)
    assert path.endswith("test_invoice.pdf")

    # Check manifest
    reports = manager.list_reports()
    assert len(reports) == 1
    assert reports[0]['filename'] == "test_invoice.pdf"
    assert reports[0]['invoice_number'] == "TEST-001"

    shutil.rmtree("test_output")


def test_save_multiple_pdfs():
    manager = FileManager("test_output")
    generator = PDFGenerator()

    # Save first PDF
    customer = Customer(name="User1", address="Addr1")
    invoice1 = Invoice(invoice_number="INV-001", date="2023-10-01", customer=customer, line_items=[])
    pdf1 = generator.generate_pdf("invoice.html", invoice1)
    path1 = manager.save_pdf(pdf1, "inv-001.pdf", {'invoice_number': 'INV-001'})

    # Save second PDF
    customer2 = Customer(name="User2", address="Addr2")
    invoice2 = Invoice(invoice_number="INV-002", date="2023-10-02", customer=customer2, line_items=[])
    pdf2 = generator.generate_pdf("invoice.html", invoice2)
    path2 = manager.save_pdf(pdf2, "inv-002.pdf", {'invoice_number': 'INV-002'})

    # Check
    reports = manager.list_reports()
    assert len(reports) == 2
    filenames = [r['filename'] for r in reports]
    assert "inv-001.pdf" in filenames
    assert "inv-002.pdf" in filenames

    shutil.rmtree("test_output")


def test_filename_collision():
    manager = FileManager("test_output")
    generator = PDFGenerator()
    customer = Customer(name="Test", address="Test")
    invoice = Invoice(invoice_number="COLLISION", date="2023-10-01", customer=customer, line_items=[])
    pdf = generator.generate_pdf("invoice.html", invoice)

    # Save first
    path1 = manager.save_pdf(pdf, "collision.pdf", {'invoice_number': 'COLLISION'})

    # Save second with same name
    path2 = manager.save_pdf(pdf, "collision.pdf", {'invoice_number': 'COLLISION2'})

    # Should have different names
    assert path1 != path2
    assert "collision.pdf" in path1
    assert "collision.pdf" in path2
    assert len([name for name in os.listdir(os.path.dirname(path2)) if "collision.pdf" in name]) == 2

    shutil.rmtree("test_output")


def test_list_reports_filtering():
    manager = FileManager("test_output")
    generator = PDFGenerator()

    # Save PDFs in different months
    customer = Customer(name="Test", address="Test")
    invoice1 = Invoice(invoice_number="FILTER1", date="2023-09-01", customer=customer, line_items=[])
    pdf1 = generator.generate_pdf("invoice.html", invoice1)
    manager.save_pdf(pdf1, "filter1.pdf", {'invoice_number': 'FILTER1', 'year': 2023, 'month': 9})

    invoice2 = Invoice(invoice_number="FILTER2", date="2023-10-01", customer=customer, line_items=[])
    pdf2 = generator.generate_pdf("invoice.html", invoice2)
    manager.save_pdf(pdf2, "filter2.pdf", {'invoice_number': 'FILTER2', 'year': 2023, 'month': 10})

    # Filter by month
    sept_reports = manager.list_reports(month=9)
    assert len(sept_reports) == 1
    assert sept_reports[0]['filename'] == "filter1.pdf"

    oct_reports = manager.list_reports(month=10)
    assert len(oct_reports) == 1
    assert oct_reports[0]['filename'] == "filter2.pdf"

    all_reports = manager.list_reports()
    assert len(all_reports) == 2

    shutil.rmtree("test_output")


def test_retrieve_and_delete():
    manager = FileManager("test_output")
    generator = PDFGenerator()
    customer = Customer(name="Test", address="Test")
    invoice = Invoice(invoice_number="DELETE", date="2023-10-01", customer=customer, line_items=[])
    pdf = generator.generate_pdf("invoice.html", invoice)
    manager.save_pdf(pdf, "delete_me.pdf", {'invoice_number': 'DELETE'})

    # Retrieve
    path = manager.get_report_path("delete_me.pdf")
    assert path is not None
    content = manager.get_report_content("delete_me.pdf")
    assert content is not None
    assert isinstance(content, bytes)

    # Delete
    assert manager.delete_report("delete_me.pdf")
    assert manager.get_report_path("delete_me.pdf") is None
    assert len(manager.list_reports()) == 0

    shutil.rmtree("test_output")


if __name__ == "__main__":
    test_save_pdf_and_manifest()
    test_save_multiple_pdfs()
    test_filename_collision()
    test_list_reports_filtering()
    test_retrieve_and_delete()
    print("Storage tests passed!")