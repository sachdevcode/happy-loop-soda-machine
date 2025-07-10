from sqlmodel import SQLModel, create_engine, Session
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from app.config import settings

engine = create_engine(
    settings.database_url,
    echo=settings.debug,  # Set to False in production
    connect_args={"check_same_thread": False}
)

def create_db_and_tables():
    """Create database and tables"""
    SQLModel.metadata.create_all(engine)

def get_session():
    """Get database session"""
    with Session(engine) as session:
        yield session

async def init_db():
    """Initialize database on startup"""
    create_db_and_tables() 