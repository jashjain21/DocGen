import pytest
from src.schema import Customer, LineItem, Invoice


def test_customer_creation():
    customer = Customer(name="John Doe", address="123 Main St")
    assert customer.name == "John Doe"
    assert customer.address == "123 Main St"


def test_line_item_creation():
    item = LineItem(description="Widget", quantity=2, unit_price=10.0)
    assert item.description == "Widget"
    assert item.quantity == 2
    assert item.unit_price == 10.0


def test_line_item_quantity_validation():
    with pytest.raises(ValueError, match="Quantity must be positive"):
        LineItem(description="Widget", quantity=0, unit_price=10.0)
    with pytest.raises(ValueError, match="Quantity must be positive"):
        LineItem(description="Widget", quantity=-1, unit_price=10.0)


def test_line_item_price_validation():
    with pytest.raises(ValueError, match="Unit price cannot be negative"):
        LineItem(description="Widget", quantity=2, unit_price=-5.0)


def test_invoice_creation_and_total():
    customer = Customer(name="Jane Smith", address="456 Elm St")
    items = [
        LineItem(description="Item 1", quantity=1, unit_price=20.0),
        LineItem(description="Item 2", quantity=3, unit_price=5.0)
    ]
    invoice = Invoice(
        invoice_number="INV-001",
        date="2023-10-01",
        customer=customer,
        line_items=items
    )
    assert invoice.invoice_number == "INV-001"
    assert invoice.date == "2023-10-01"
    assert invoice.customer.name == "Jane Smith"
    assert len(invoice.line_items) == 2
    assert invoice.total_amount == 35.0  # 1*20 + 3*5


def test_invoice_empty_line_items():
    customer = Customer(name="Test", address="Test Addr")
    invoice = Invoice(
        invoice_number="INV-002",
        date="2023-10-02",
        customer=customer,
        line_items=[]
    )
    assert invoice.total_amount == 0.0