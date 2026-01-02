from sqlmodel import Session, select
from models.weather import *

def fetch_location_map(session: Session):
    statement = select(Dim_Location.location_name, Dim_Location.sk)
    results = session.exec(statement).all()
    return {name: sk for name, sk in results}