from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from typing import List
from datetime import datetime

from app.database import get_session
from app.models import Product, Transaction, PurchaseRequest, PurchaseResponse
from app.ai_parser import parse_purchase_request
from app.seed_data import get_available_products

router = APIRouter()

@router.get("/inventory", response_model=List[Product])
async def get_inventory(session: Session = Depends(get_session)):
    """Get current inventory"""
    products = session.exec(select(Product)).all()
    return products

@router.get("/transactions", response_model=List[Transaction])
async def get_transactions(session: Session = Depends(get_session)):
    """Get transaction history"""
    transactions = session.exec(select(Transaction)).all()
    return transactions

@router.post("/purchase", response_model=PurchaseResponse)
async def purchase_soda(request: PurchaseRequest, session: Session = Depends(get_session)):
    """Process natural language purchase request"""
    try:
        
        available_products = get_available_products()
        
        
        intent = parse_purchase_request(request.message, available_products)
        
        
        if intent.intent.value == "query":
            products = session.exec(select(Product)).all()
            product_list = [f"{p.name} (${p.price}) - {p.stock} in stock" for p in products]
            return PurchaseResponse(
                success=True,
                message=f"Available products: {', '.join(product_list)}",
                product_name=None,
                quantity=None,
                total_amount=None,
                remaining_stock=None
            )
        
        elif intent.intent.value == "refuse":
            return PurchaseResponse(
                success=True,
                message="No problem! Let me know if you change your mind.",
                product_name=None,
                quantity=None,
                total_amount=None,
                remaining_stock=None
            )
        
        elif intent.intent.value == "cancel":
            return PurchaseResponse(
                success=True,
                message="Transaction cancelled. Is there anything else I can help you with?",
                product_name=None,
                quantity=None,
                total_amount=None,
                remaining_stock=None
            )
        
        elif intent.intent.value == "unknown":
            return PurchaseResponse(
                success=False,
                message="I'm not sure what you want to do. You can ask about our products or try to make a purchase.",
                product_name=None,
                quantity=None,
                total_amount=None,
                remaining_stock=None
            )
        
        elif intent.intent.value == "purchase":
            if not intent.product_name:
                return PurchaseResponse(
                    success=False,
                    message="I couldn't understand which product you want to buy. Available products: " + ", ".join(available_products)
                )
            
            if not intent.quantity or intent.quantity <= 0:
                return PurchaseResponse(
                    success=False,
                    message="Please specify a valid quantity to purchase."
                )
            
            
            product = session.exec(select(Product).where(Product.name == intent.product_name)).first()
            if not product:
                return PurchaseResponse(
                    success=False,
                    message=f"Product '{intent.product_name}' not found. Available products: " + ", ".join(available_products)
                )
            
            
            if product.stock < intent.quantity:
                return PurchaseResponse(
                    success=False,
                    message=f"Sorry, only {product.stock} {product.name} available. You requested {intent.quantity}."
                )
            
            
            total_amount = product.price * intent.quantity
            
            
            product.stock -= intent.quantity
            product.updated_at = datetime.utcnow()
            
            
            transaction = Transaction(
                product_id=product.id,
                quantity=intent.quantity,
                total_amount=total_amount,
                payment_method="cash",
                status="completed"
            )
            
            session.add(transaction)
            session.add(product)  
            session.commit()
            session.refresh(product)  
            
            return PurchaseResponse(
                success=True,
                message=f"Successfully purchased {intent.quantity} {product.name} for ${total_amount:.2f}",
                product_name=product.name,
                quantity=intent.quantity,
                total_amount=total_amount,
                remaining_stock=product.stock
            )
        
        else:
            return PurchaseResponse(
                success=False,
                message="I couldn't understand your request. Please try again."
            )
            
    except Exception as e:
        return PurchaseResponse(
            success=False,
            message=f"Error processing request: {str(e)}"
        ) 