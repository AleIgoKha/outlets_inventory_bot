import os
from dotenv import load_dotenv
from sqlalchemy import String, Numeric, ForeignKey, Boolean, Integer, DateTime, func
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncAttrs
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import ARRAY

from decimal import Decimal
from datetime import datetime


load_dotenv()
engine = create_async_engine(url=os.getenv('DB_URL'))

async_session = async_sessionmaker(engine)

class Base(AsyncAttrs, DeclarativeBase):
    pass

# База данных с продукцией
class Product(Base):
    __tablename__ = 'products'
    
    product_id: Mapped[int] = mapped_column(primary_key=True)
    product_name: Mapped[str] = mapped_column(String)
    product_unit: Mapped[str] = mapped_column(String(5))
    product_price: Mapped[Decimal] = mapped_column(Numeric(10, 2))
    
    stocks: Mapped[list["Stock"]] = relationship(back_populates="product", cascade="all, delete-orphan")
    

# База данных с торговыми точками
class Outlet(Base):
    __tablename__ = 'outlets'
    
    outlet_id: Mapped[int] = mapped_column(primary_key=True)
    outlet_name: Mapped[str] = mapped_column(String, nullable=False)
    outlet_descr: Mapped[str] = mapped_column(String, nullable=True)
    outlet_arch: Mapped[bool] = mapped_column(Boolean, default=False)
    
    stocks: Mapped[list["Stock"]] = relationship(back_populates="outlet", cascade="all, delete-orphan")
    transactions: Mapped[list["Transaction"]] = relationship(back_populates="outlet", cascade="all, delete-orphan")
    reports: Mapped[list["Report"]] = relationship(back_populates="outlet", cascade="all, delete-orphan")
    
class Stock(Base):
    __tablename__ = 'stocks'
    
    stock_id: Mapped[int] = mapped_column(primary_key=True)
    outlet_id: Mapped[int] = mapped_column(ForeignKey('outlets.outlet_id', ondelete='CASCADE'))
    product_id: Mapped[int] = mapped_column(ForeignKey('products.product_id', ondelete='CASCADE'))
    stock_qty: Mapped[Decimal] = mapped_column(Numeric(11, 3), default=Decimal("0.000"))
    stock_active: Mapped[bool] = mapped_column(Boolean, default=True)
    # Можно в будущем будет добавить касмотную цену и название товара для конкретной сессии для гибкости
    
    outlet: Mapped["Outlet"] = relationship(back_populates="stocks")
    product: Mapped["Product"] = relationship(back_populates="stocks")
    
    
class Transaction(Base):
    __tablename__ = 'transactions'
    
    transaction_id: Mapped[int] = mapped_column(primary_key=True)
    outlet_id: Mapped[int] = mapped_column(ForeignKey('outlets.outlet_id', ondelete='CASCADE'))
    stock_id: Mapped[int] = mapped_column(ForeignKey('stocks.stock_id'))
    transaction_datetime: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    transaction_type: Mapped[str] = mapped_column(String)
    transaction_product_name: Mapped[str] = mapped_column(String)
    product_qty: Mapped[Decimal] = mapped_column(Numeric(9, 3))
    transaction_product_price: Mapped[Decimal] = mapped_column(Numeric(9, 2))
    balance_after: Mapped[Decimal] = mapped_column(Numeric(9, 3), nullable=True)
    transaction_info: Mapped[list[Decimal] | None] = mapped_column(ARRAY(Numeric(9, 3)), nullable=True)
    transaction_note: Mapped[str | None] = mapped_column(String, nullable=True)
    
    outlet: Mapped["Outlet"] = relationship(back_populates="transactions")
    
    
class Report(Base):
    __tablename__ = 'reports'
    
    report_id: Mapped[int] = mapped_column(primary_key=True)
    outlet_id: Mapped[int] = mapped_column(ForeignKey('outlets.outlet_id', ondelete='CASCADE'))
    report_datetime: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    report_purchases: Mapped[int] = mapped_column(Integer)
    report_revenue: Mapped[Decimal] = mapped_column(Numeric(9, 2))
    report_note: Mapped[str | None] = mapped_column(String, nullable=True)
    
    outlet: Mapped["Outlet"] = relationship(back_populates="reports")

async def async_main():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)