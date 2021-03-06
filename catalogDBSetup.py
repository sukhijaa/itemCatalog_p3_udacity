import random
import string
from itsdangerous import (TimedJSONWebSignatureSerializer as Serializer,
                          BadSignature, SignatureExpired)
from passlib.apps import custom_app_context as pwd_context
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()
secret_key = ''.join(
    random.choice(string.ascii_uppercase + string.digits) for x in range(32))

DB_CONNECT_STRING = 'postgresql://postgres:postgres@localhost/postgres'

class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    username = Column(String(32), index=True)
    picture = Column(String)
    email = Column(String)
    password_hash = Column(String)

    def hash_password(self, password):
        self.password_hash = pwd_context.encrypt(password)

    def verify_password(self, password):
        return pwd_context.verify(password, self.password_hash)

    def generate_auth_token(self, expiration=6000):
        s = Serializer(secret_key, expires_in=expiration)
        return s.dumps({'id': self.id})

    @staticmethod
    def verify_auth_token(token):
        s = Serializer(secret_key)
        try:
            print('In verify token')
            data = s.loads(token)
            print(data)
            print(str(data))
        except SignatureExpired as se:
            # Valid Token, but expired
            print('Session expired. Asking user to re-login')
            print(se)
            return None
        except BadSignature as bs:
            # Invalid Token
            print('Bad Signature. Asking user to re-login')
            return None
        user_id = data['id']
        return user_id


class Category(Base):
    __tablename__ = 'categories'

    id = Column(Integer, primary_key=True)
    name = Column(String(60), nullable=False)
    description = Column(String(250))
    creator_id = Column(Integer, ForeignKey('user.id'))
    creator = relationship(User)

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
            'name': self.name,
            'id': self.id,
            'description': self.description
        }


class CatalogItem(Base):
    __tablename__ = 'catalog_item'

    name = Column(String(80), nullable=False)
    id = Column(Integer, primary_key=True)
    description = Column(String(250))
    categoryId = Column(Integer, ForeignKey('categories.id'))
    category = relationship(Category)
    creator_id = Column(Integer, ForeignKey('user.id'))
    creator = relationship(User)

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
            'name': self.name,
            'description': self.description,
            'id': self.id,
            'categoryId': self.category_id,
        }


engine = create_engine(DB_CONNECT_STRING)

Base.metadata.create_all(engine)
