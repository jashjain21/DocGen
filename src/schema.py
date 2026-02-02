from pydantic import BaseModel, field_validator, computed_field


class Customer(BaseModel):
    name: str
    address: str


class LineItem(BaseModel):
    description: str
    quantity: int
    unit_price: float

    @field_validator('quantity')
    @classmethod
    def quantity_positive(cls, v):
        if v <= 0:
            raise ValueError('Quantity must be positive')
        return v

    @field_validator('unit_price')
    @classmethod
    def price_non_negative(cls, v):
        if v < 0:
            raise ValueError('Unit price cannot be negative')
        return v


class Invoice(BaseModel):
    invoice_number: str
    date: str
    customer: Customer
    line_items: list[LineItem]

    @computed_field
    def total_amount(self) -> float:
        return sum(item.quantity * item.unit_price for item in self.line_items)