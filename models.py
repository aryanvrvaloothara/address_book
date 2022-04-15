from sqlalchemy import Column, Integer, String, ForeignKey

from db import Base


class User(Base):

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    password = Column(String)

    # address = relationship("AddressBook", back_populates="user")


class AddressBook(Base):

    __tablename__ = "address_book"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    house_name = Column(String, index=True)
    place = Column(String, index=True)
    post_office = Column(String, index=True)
    pin_code = Column(String, index=True)
    latitude = Column(String, index=True)
    longitude = Column(String, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    # user = relationship("User", back_populates="address")
