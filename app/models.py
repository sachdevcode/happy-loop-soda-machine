from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime
from typing import Optional, List, TYPE_CHECKING
from pydantic import validator

if TYPE_CHECKING:
    from app.models import Transaction as TransactionType

class Product(SQLModel, table=True):
    """Product model for soda inventory"""
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True, max_length=100)
    price: float = Field(ge=0, description="Price in dollars")
    stock: int = Field(ge=0, default=0, description="Available stock quantity")
    description: Optional[str] = Field(default=None, max_length=500)
    category: str = Field(default="soda", max_length=50)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    

    transactions: List["Transaction"] = Relationship(back_populates="product")
    
    @validator('name')
    def validate_name(cls, v):
        if not v.strip():
            raise ValueError('Product name cannot be empty')
        return v.strip().lower()
    
    @validator('price')
    def validate_price(cls, v):
        if v < 0:
            raise ValueError('Price cannot be negative')
        return round(v, 2)

class Transaction(SQLModel, table=True):
    """Transaction model for purchase history"""
    id: Optional[int] = Field(default=None, primary_key=True)
    product_id: int = Field(foreign_key="product.id")
    quantity: int = Field(ge=1, description="Quantity purchased")
    total_amount: float = Field(ge=0, description="Total amount paid")
    payment_method: str = Field(default="cash", max_length=20)
    status: str = Field(default="completed", max_length=20)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    

    product: Optional["Product"] = Relationship(back_populates="transactions")
    
    @validator('quantity')
    def validate_quantity(cls, v):
        if v <= 0:
            raise ValueError('Quantity must be positive')
        return v
    
    @validator('total_amount')
    def validate_total_amount(cls, v):
        if v < 0:
            raise ValueError('Total amount cannot be negative')
        return round(v, 2)

class PurchaseRequest(SQLModel):
    """Request model for purchase endpoint"""
    message: str = Field(..., description="Natural language purchase request")
    
    @validator('message')
    def validate_message(cls, v):
        if not v.strip():
            raise ValueError('Message cannot be empty')
        return v.strip()

class PurchaseResponse(SQLModel):
    """Response model for purchase endpoint"""
    success: bool
    message: str
    product_name: Optional[str] = None
    quantity: Optional[int] = None
    total_amount: Optional[float] = None
    remaining_stock: Optional[int] = None 