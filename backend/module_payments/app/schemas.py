# /module_payments/app/schemas.py
from pydantic import BaseModel, Field
from typing import Optional, List, Dict

class ItemDetails(BaseModel):
    id: str
    price: int
    quantity: int
    name: str

class CustomerDetails(BaseModel):
    first_name: str
    last_name: Optional[str] = None
    email: str
    phone: str

class CreateTransactionRequest(BaseModel):
    order_id: str = Field(..., description="ID Pesanan Unik dari sistem Anda")
    gross_amount: int = Field(..., description="Total harga dalam Rupiah (integer)")
    items: List[ItemDetails] = Field(..., description="Detail item pesanan")
    customer: CustomerDetails = Field(..., description="Detail pelanggan")

class CreateTransactionResponse(BaseModel):
    order_id: str
    transaction_token: str
    redirect_url: Optional[str] = None # Untuk metode redirect