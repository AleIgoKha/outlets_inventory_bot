from aiogram.fsm.state import StatesGroup, State


class Outlet(StatesGroup):
    name = State()
    change_name = State()
    description = State()
    change_description = State()
    delete = State()
    
    
class Stock(StatesGroup):
    replenishment = State()
    writeoff = State()
    selling = State()
    balance = State()
    rollback_balance = State()

    
class Transaction(StatesGroup):
    time = State()
    rollback = State()
    
    
class Report(StatesGroup):
    purchases = State()
    revenue = State()
    note = State()
    purchases_only = State()
    revenue_only = State()
    note_only = State()