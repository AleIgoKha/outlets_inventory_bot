import pytz
from sqlalchemy import select, delete, func, desc
from sqlalchemy.orm import selectinload
from decimal import Decimal
from datetime import datetime

from app.database.models import Transaction, Stock
from app.com_func import with_session, get_utc_day_bounds


# последняя транзакция с товаром торговой точки по типу транзакции
@with_session()
async def get_last_transaction(session, outlet_id, stock_id):
    
    max_datetime = select(func.max(Transaction.transaction_datetime)) \
                    .where(Transaction.outlet_id == outlet_id,
                            Transaction.stock_id == stock_id).scalar_subquery()
    
    stmt = select(Transaction) \
            .where(Transaction.outlet_id == outlet_id,
                   Transaction.stock_id == stock_id,
                   Transaction.transaction_datetime == max_datetime)
    
    last_transaction = await session.scalar(stmt)
    
    if last_transaction is not None:
        last_transaction_data = {
            'transaction_id': last_transaction.transaction_id,
            'outlet_id': last_transaction.outlet_id,
            'stock_id': last_transaction.stock_id,
            'transaction_datetime': last_transaction.transaction_datetime,
            'transaction_type': last_transaction.transaction_type,
            'transaction_product_name': last_transaction.transaction_product_name,
            'product_qty': last_transaction.product_qty,
            'transaction_product_price': last_transaction.transaction_product_price,
            'balance_after': last_transaction.balance_after,
            'transaction_info': last_transaction.transaction_info,
            'transaction_note': last_transaction.transaction_note
            }
    else:
        last_transaction_data = None
    
    return last_transaction_data


# последняя транзакция с товаром торговой точки по типу транзакции
@with_session()
async def get_last_balance_transaction(session, outlet_id, stock_id):
    
    max_datetime = select(func.max(Transaction.transaction_datetime)) \
                    .where(Transaction.outlet_id == outlet_id,
                           Transaction.transaction_type == 'balance',
                           Transaction.stock_id == stock_id).scalar_subquery()
    
    stmt = select(Transaction) \
            .where(Transaction.outlet_id == outlet_id,
                   Transaction.stock_id == stock_id,
                   Transaction.transaction_type == 'balance',
                   Transaction.transaction_datetime == max_datetime)
    
    last_transaction = await session.scalar(stmt)
    
    if last_transaction is not None:
        last_transaction_data = {
            'transaction_id': last_transaction.transaction_id,
            'outlet_id': last_transaction.outlet_id,
            'stock_id': last_transaction.stock_id,
            'transaction_datetime': last_transaction.transaction_datetime,
            'transaction_type': last_transaction.transaction_type,
            'transaction_product_name': last_transaction.transaction_product_name,
            'product_qty': last_transaction.product_qty,
            'transaction_product_price': last_transaction.transaction_product_price,
            'balance_after': last_transaction.balance_after,
            'transaction_info': last_transaction.transaction_info,
            'transaction_note': last_transaction.transaction_note
            }
    else:
        last_transaction_data = None
    
    return last_transaction_data


# проводим транзакцию пополнения товара
@with_session(commit=True)
async def transaction_replenish(session, outlet_id, product_id, product_qty, added_pieces: list=None, transaction_datetime: datetime=None):
    if product_qty <= 0:
        raise ValueError("Replenishment quantity must be positive.")
    
    stock_data = await session.scalar(
        select(Stock)
        .options(selectinload(Stock.product))
        .where(Stock.outlet_id == outlet_id, Stock.product_id == product_id)
        .with_for_update()
    )
    
    if not stock_data:
        raise ValueError(f"Stock for product ID {product_id} at outlet ID {outlet_id} not found.")
    
    current_qty = stock_data.stock_qty
    new_qty = current_qty + Decimal(product_qty)
    
    # Update stock quantity
    stock_data.stock_qty = new_qty
    
    
    transaction_data = Transaction(
        transaction_datetime=transaction_datetime,
        outlet_id=outlet_id,
        stock_id=stock_data.stock_id,
        transaction_type='replenishment',
        transaction_product_name=stock_data.product.product_name,
        product_qty=product_qty,
        transaction_product_price=stock_data.product.product_price,
        balance_after=new_qty,
        transaction_info=added_pieces,
        transaction_note=None
    )
    
    # добавляем транзакцию
    session.add(transaction_data)


# проводим транзакцию списания товара
@with_session(commit=True)
async def transaction_writeoff(session, outlet_id, product_id, product_qty, added_pieces: list=None, transaction_datetime: datetime=None):
    if product_qty <= 0:
        raise ValueError("Replenishment quantity must be positive.")
    
    stock_data = await session.scalar(
        select(Stock) \
        .options(selectinload(Stock.product))
        .where(Stock.outlet_id == outlet_id, Stock.product_id == product_id)
        .with_for_update()
    )
    
    if not stock_data:
        raise ValueError(f"Stock for product ID {product_id} at outlet ID {outlet_id} not found.")
    
    current_qty = stock_data.stock_qty
    new_qty = current_qty - Decimal(product_qty)
    
    if new_qty < 0:
        raise ValueError("Stock quantity must be positive or at least zero.")
    
    # Update stock quantity
    stock_data.stock_qty = new_qty

    transaction_data = Transaction(
        transaction_datetime=transaction_datetime,
        outlet_id=outlet_id,
        stock_id=stock_data.stock_id,
        transaction_type='writeoff',
        transaction_product_name=stock_data.product.product_name,
        product_qty=Decimal(product_qty),
        transaction_product_price=stock_data.product.product_price,
        balance_after=new_qty,
        transaction_info=added_pieces,
        transaction_note=None
    )
    
    # добавляем транзакцию
    session.add(transaction_data)
    
    
# проводим транзакцию списания товара и удаляем товар из торговой точки
@with_session(commit=True)
async def transaction_delete_product(session, outlet_id, product_id):   
    stock_data = await session.scalar(
        select(Stock) \
        .options(selectinload(Stock.product))
        .where(Stock.outlet_id == outlet_id, Stock.product_id == product_id)
        .with_for_update()
    )
    
    if not stock_data:
        raise ValueError(f"Stock for product ID {product_id} at outlet ID {outlet_id} not found.")
    
    stock_data.stock_qty = Decimal(0)
    stock_data.stock_active = False
    
    transaction_data = Transaction(
        outlet_id=outlet_id,
        stock_id=stock_data.stock_id,
        transaction_type='writeoff',
        transaction_product_name=stock_data.product.product_name,
        product_qty=stock_data.stock_qty,
        transaction_product_price=stock_data.product.product_price,
        balance_after=Decimal(0),
        transaction_info=None,
        transaction_note=None
    )
    
    # добавляем транзакцию
    session.add(transaction_data)


# проводим транзакцию списания товара
@with_session(commit=True)
async def transaction_selling(session, outlet_id, added_products):
    
    for product_id in added_products.keys():
        added_pieces = [Decimal(added_piece) for added_piece in added_products[product_id]]
        product_qty = sum(added_pieces)
        product_id = int(product_id)
        
        if product_qty <= 0:
            raise ValueError("Replenishment quantity must be positive.")
        
        stock_data = await session.scalar(
            select(Stock) \
            .options(selectinload(Stock.product))
            .where(Stock.outlet_id == outlet_id, Stock.product_id == product_id)
            .with_for_update()
    )
        
        if not stock_data:
            raise ValueError(f"Stock for product ID {product_id} at outlet ID {outlet_id} not found.")
        
        product_unit = stock_data.product.product_unit
        
        if product_unit == 'кг':
            product_qty = product_qty / Decimal(1000)
            added_pieces = [added_piece / Decimal(1000) for added_piece in added_pieces]
        
        current_qty = stock_data.stock_qty
        new_qty = current_qty - Decimal(product_qty)
        
        if new_qty < 0:
            raise ValueError("Stock quantity cannot be lower than product quantity.")
        
        # Update stock quantity
        stock_data.stock_qty = new_qty
        
        transaction_data = Transaction(
            outlet_id=outlet_id,
            stock_id=stock_data.stock_id,
            transaction_type='selling',
            transaction_product_name=stock_data.product.product_name,
            product_qty=Decimal(product_qty),
            transaction_product_price=stock_data.product.product_price,
            balance_after=new_qty,
            transaction_info=added_pieces,
            transaction_note=None
        )
        
        # добавляем транзакцию
        session.add(transaction_data)


# проводим транзакцию продажи по балансу
@with_session(commit=True)
async def transaction_balance(session, outlet_id, product_id, product_qty, added_pieces: list=None, transaction_datetime: datetime=None):
    if product_qty < 0:
        raise ValueError("Replenishment quantity must be positive or zero.")
    
    stock_data = await session.scalar(
        select(Stock) \
        .options(selectinload(Stock.product))
        .where(Stock.outlet_id == outlet_id, Stock.product_id == product_id)
        .with_for_update()
    )
    
    if not stock_data:
        raise ValueError(f"Stock for product ID {product_id} at outlet ID {outlet_id} not found.")
    
    current_qty = stock_data.stock_qty
    qty_diff = current_qty - Decimal(product_qty)
    
    if Decimal(product_qty) < 0:
        raise ValueError("Stock quantity must be positive or at least zero.")
    
    # Update stock quantity
    stock_data.stock_qty = Decimal(product_qty)
    
    transaction_data = Transaction(
        transaction_datetime=transaction_datetime,
        outlet_id=outlet_id,
        stock_id=stock_data.stock_id,
        transaction_type='balance',
        transaction_product_name=stock_data.product.product_name,
        product_qty=qty_diff,
        transaction_product_price=stock_data.product.product_price,
        balance_after=Decimal(product_qty),
        transaction_info=added_pieces,
        transaction_note=None
    )
    
    # добавляем транзакцию
    session.add(transaction_data)


# проверяет наличие указанных транзакций совершенных с запасами продукта за указанную дату
@with_session()
async def were_stock_transactions(session, stock_id, date_time, transaction_types: list):
    start, end = get_utc_day_bounds(date_time)
    
    stmt = select(
        func.count(Transaction.transaction_id) > 0
    ).where(
        Transaction.stock_id == stock_id,
        Transaction.transaction_type.in_(transaction_types),
        Transaction.transaction_datetime >= start,
        Transaction.transaction_datetime < end
    )

    result = await session.scalar(stmt)
    
    return result


# проверяет наличие указанных транзакций совершенных в торговой точке за указанную дату
@with_session()
async def were_outlet_transactions(session, outlet_id, date_time, transaction_types: list):
    start, end = get_utc_day_bounds(date_time)

    stmt = select(
        func.count(Transaction.transaction_id) > 0
    ).where(
        Transaction.outlet_id == outlet_id,
        Transaction.transaction_type.in_(transaction_types),
        Transaction.transaction_datetime >= start,
        Transaction.transaction_datetime < end
    )

    result = await session.scalar(stmt)
    return result


# откат транзакции продажи и баланса
@with_session(commit=True)
async def rollback_selling(session, transaction_id, stock_id):
    
    transaction_data = await session.scalar(select(Transaction).where(Transaction.transaction_id == transaction_id))
    
    if not transaction_data:
        raise ValueError(f"Transaction {transaction_id} not found.")
    
    stock_data = await session.scalar(select(Stock).where(Stock.stock_id == stock_id).with_for_update())
    
    if not stock_data:
        raise ValueError(f"Stock {stock_id} not found.")
    
    stock_data.stock_qty += transaction_data.product_qty
    stock_data.stock_active = True
    
    await session.execute(delete(Transaction).where(Transaction.transaction_id == transaction_id))
    

# откат транзакции пополнения
@with_session(commit=True)
async def rollback_replenishment(session, transaction_id):
    
    transaction_data = await session.scalar(select(Transaction).where(Transaction.transaction_id == transaction_id))
    
    if not transaction_data:
        raise ValueError(f"Transaction {transaction_id} not found.")
    
    stock_data = await session.scalar(select(Stock).where(Stock.stock_id == transaction_data.stock_id).with_for_update())
    
    if not stock_data:
        raise ValueError(f"Stock {transaction_data.stock_id} not found.")
    
    stock_data.stock_qty -= transaction_data.product_qty
    stock_data.stock_active = True
    
    await session.execute(delete(Transaction).where(Transaction.transaction_id == transaction_id))
    
    
# откат транзакции продажи
@with_session(commit=True)
async def rollback_writeoff(session, transaction_id):
    
    transaction_data = await session.scalar(select(Transaction).where(Transaction.transaction_id == transaction_id))
    
    if not transaction_data:
        raise ValueError(f"Transaction {transaction_id} not found.")
    
    stock_data = await session.scalar(select(Stock).where(Stock.stock_id == transaction_data.stock_id).with_for_update())
    
    if not stock_data:
        raise ValueError(f"Stock {transaction_data.stock_id} not found.")
    
    stock_data.stock_qty += transaction_data.product_qty
    stock_data.stock_active = True
    
    await session.execute(delete(Transaction).where(Transaction.transaction_id == transaction_id))


# информация о транзакциях товара в торговой точке
@with_session()
async def transactions_info(session, outlet_id, stock_id):
    
    stmt = select(Transaction) \
            .where(Transaction.outlet_id == outlet_id,
                   Transaction.stock_id == stock_id) \
            .order_by(desc(Transaction.transaction_datetime))
    
    transactions = await session.scalars(stmt)
    
    if transactions is not None:
        transactions_data = [{
            'transaction_id': transaction.transaction_id,
            'outlet_id': transaction.outlet_id,
            'stock_id': transaction.stock_id,
            'transaction_datetime': transaction.transaction_datetime,
            'transaction_type': transaction.transaction_type,
            'transaction_product_name': transaction.transaction_product_name,
            'product_qty': transaction.product_qty,
            'transaction_product_price': transaction.transaction_product_price,
            'balance_after': transaction.balance_after,
            'transaction_info': transaction.transaction_info,
            'transaction_note': transaction.transaction_note
            } for transaction in transactions]
    else:
        transactions_data = None
    
    return transactions_data


# информация об одной транзакции
@with_session()
async def transaction_info(session, transaction_id):
    
    stmt = select(Transaction) \
            .where(Transaction.transaction_id == transaction_id)
    
    transaction = await session.scalar(stmt)
    
    if transaction is not None:
        transaction_data = {
            'transaction_id': transaction.transaction_id,
            'outlet_id': transaction.outlet_id,
            'stock_id': transaction.stock_id,
            'transaction_datetime': transaction.transaction_datetime,
            'transaction_type': transaction.transaction_type,
            'transaction_product_name': transaction.transaction_product_name,
            'product_qty': transaction.product_qty,
            'transaction_product_price': transaction.transaction_product_price,
            'balance_after': transaction.balance_after,
            'transaction_info': transaction.transaction_info,
            'transaction_note': transaction.transaction_note
            }
    else:
        transaction_data = None
    
    return transaction_data



# число транзакций остатка за день
@with_session()
async def balance_transactions_number_today(session, outlet_id):
    start, end = get_utc_day_bounds(datetime.now(pytz.timezone('Europe/Chisinau')))
    
    stmt = select(func.count(Transaction.transaction_id)) \
            .where(Transaction.transaction_type == 'balance',
                   Transaction.outlet_id == outlet_id,
                   Transaction.transaction_datetime >= start,
                   Transaction.transaction_datetime < end)
    
    number = await session.scalar(stmt)
    
    return number or 0

# число транзакций остатка за день
@with_session()
async def balance_transactions_number(session, outlet_id, date_time):
    start, end = get_utc_day_bounds(date_time)
    
    stmt = select(func.count(Transaction.transaction_id)) \
            .where(Transaction.transaction_type == 'balance',
                   Transaction.outlet_id == outlet_id,
                   Transaction.transaction_datetime >= start,
                   Transaction.transaction_datetime < end)
    
    number = await session.scalar(stmt)
    
    return number or 0


# информация о транзакциях товара в торговой точке
@with_session()
async def get_expected_revenue(session, outlet_id, date_time):
    start, end = get_utc_day_bounds(date_time)
    
    stmt = select(func.sum(Transaction.transaction_product_price * Transaction.product_qty)) \
            .where(Transaction.transaction_type == 'balance',
                   Transaction.outlet_id == outlet_id,
                   Transaction.transaction_datetime >= start,
                   Transaction.transaction_datetime < end)
    
    expected_revenue = await session.scalar(stmt)
    
    return expected_revenue