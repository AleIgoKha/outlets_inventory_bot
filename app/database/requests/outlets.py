from sqlalchemy import select, update, asc, delete

from app.com_func import with_session 
from app.database.models import Outlet


@with_session(commit=True)
async def add_outlet(session, outlet_data):
    session.add(Outlet(**outlet_data))


@with_session()
async def get_outlets(session):
    result = await session.scalars(select(Outlet).order_by(asc(Outlet.outlet_name)))
    return result.all()


@with_session()
async def get_outlet(session, outlet_id):
    outlet_data = await session.scalar(select(Outlet).where(Outlet.outlet_id == outlet_id))
    return {
        'outlet_id': outlet_data.outlet_id,
        'outlet_name': outlet_data.outlet_name,
        'outlet_descr': outlet_data.outlet_descr,
        'outlet_arch': outlet_data.outlet_arch
    }
    
# изменяем данные торговой точки
@with_session(commit=True)
async def change_outlet_data(session, outlet_id, outlet_data):
    await session.execute(update(Outlet).where(Outlet.outlet_id == outlet_id).values(outlet_data))
    
    
# удаление торговой точки
@with_session(commit=True)
async def delete_outlet(session, outlet_id):
    await session.execute(delete(Outlet).where(Outlet.outlet_id == outlet_id))