from sqlalchemy import select, update, asc, or_

from app.database.models import Product, Stock
from app.com_func import with_session


# добавление продукта в запасы торговой точки
@with_session(commit=True)
async def add_stock(session, outlet_id, product_id):
    stock_active = await session.scalar(
                                select(Stock.stock_active) \
                                .where(Stock.outlet_id == outlet_id,
                                    Stock.product_id == product_id))
    
    if stock_active is not None:
        await session.execute(update(Stock) \
                    .where(Stock.outlet_id == outlet_id,
                        Stock.product_id == product_id) \
                    .values({'stock_active': True}))
    else:
        session.add(Stock(**{
                        'outlet_id': outlet_id,
                        'product_id': product_id
                    }))


# данные всех продуктов торговой точки по ее id
@with_session()
async def get_active_stock_products(session, outlet_id):
    
    result = await session.execute(
        select(Stock, Product) \
        .join(Stock, Product.product_id == Stock.product_id) \
        .where(Stock.outlet_id == outlet_id,
               Stock.stock_active == True) \
        .order_by(asc(Product.product_name))
    )

    rows = result.all()
    
    return [
        {
            'stock_id': stock.stock_id,
            'outlet_id': stock.outlet_id,
            'product_id': stock.product_id,
            'stock_qty': stock.stock_qty,
            'stock_active': stock.stock_active,
            'product_name': product.product_name,
            'product_unit': product.product_unit,
            'product_price': product.product_price
        }
        
        for stock, product in rows
    ]


# данные всех продуктов ВНЕ торговой точки по ее id
@with_session()
async def get_out_stock_products(session, outlet_id):
    
    stmt = select(Product) \
            .outerjoin(Stock,
                        (Product.product_id == Stock.product_id) &
                        (Stock.outlet_id == outlet_id)) \
            .where(or_(Stock.stock_id.is_(None),
                        Stock.stock_active == False)) \
            .order_by(asc(Product.product_name))
    
    out_stock_products = await session.scalars(stmt)
    
    return out_stock_products.all()


# информация о продукте
@with_session()
async def get_product(session, product_id):
    product = await session.scalar(select(Product).where(Product.product_id == product_id))
    return product


# данные одного продукта по его id и id его торговой точки
@with_session()
async def get_stock_product(session, outlet_id, product_id):
    result = await session.execute(
                                select(Stock, Product) \
                                .join(Stock, Product.product_id == Stock.product_id) \
                                .where(Stock.outlet_id == outlet_id,
                                       Product.product_id == product_id)
                            )
    
    stock, product = result.first()
    
    return {
            'stock_id': stock.stock_id,
            'outlet_id': stock.outlet_id,
            'product_id': stock.product_id,
            'stock_qty': stock.stock_qty,
            'stock_active': stock.stock_active,
            'product_name': product.product_name,
            'product_unit': product.product_unit,
            'product_price': product.product_price
        }