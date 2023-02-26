import sqlalchemy
import sqlalchemy as sq
from sqlalchemy.orm import declarative_base, sessionmaker

Base = declarative_base()

class SeenUsers(Base):
    __tablename__ = "seen_users"

    id = sq.Column(sq.Integer, primary_key=True)
    vk_id = sq.Column(sq.Integer, unique=False)
    seen_user_id = sq.Column(sq.Integer, unique=False)

def create_table_seen_users(engine):
    Base.metadata.create_all(engine)


DSN = "postgresql://postgres:postgres@localhost:5432/vkorm"
engine = sqlalchemy.create_engine(DSN)
create_table_seen_users(engine)

Session = sessionmaker(bind=engine)
session = Session()

def insert_data_seen_users(vk_id, seen_user_id):
    seen_user = SeenUsers(vk_id=vk_id, seen_user_id=seen_user_id)
    session.add(seen_user)
    session.commit()

def select(vk_id, seen_user_id):
    result = session.query(SeenUsers).filter(SeenUsers.vk_id == vk_id, SeenUsers.seen_user_id == seen_user_id).first()
    session.close()
    return result

def drop_seen_users(user_id):
    session.query(SeenUsers).filter(SeenUsers.vk_id == user_id).delete()
    session.commit()
