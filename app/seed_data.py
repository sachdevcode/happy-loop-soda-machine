from sqlmodel import Session, select
from app.database import engine
from app.models import Product

def seed_products():
    """Seed the database with sample products"""
    products = [
        {
            "name": "coke",
            "price": 1.50,
            "stock": 50,
            "description": "Classic Coca-Cola",
            "category": "cola"
        },
        {
            "name": "pepsi",
            "price": 1.45,
            "stock": 45,
            "description": "Pepsi Cola",
            "category": "cola"
        },
        {
            "name": "sprite",
            "price": 1.40,
            "stock": 40,
            "description": "Lemon-lime soda",
            "category": "lemon-lime"
        },
        {
            "name": "fanta",
            "price": 1.35,
            "stock": 35,
            "description": "Orange soda",
            "category": "orange"
        },
        {
            "name": "mountain dew",
            "price": 1.55,
            "stock": 30,
            "description": "Citrus soda",
            "category": "citrus"
        },
        {
            "name": "dr pepper",
            "price": 1.60,
            "stock": 25,
            "description": "Unique blend of 23 flavors",
            "category": "unique"
        }
    ]
    
    with Session(engine) as session:
        
        existing_products = session.exec(select(Product)).all()
        if existing_products:
            print("Products already exist in database")
            return
        
        
        for product_data in products:
            product = Product(**product_data)
            session.add(product)
        
        session.commit()
        print(f"✅ Seeded {len(products)} products successfully")

def get_available_products():
    """Get list of available products for AI parsing"""
    with Session(engine) as session:
        products = session.exec(select(Product)).all()
        return [product.name for product in products]

if __name__ == "__main__":
    seed_products() 