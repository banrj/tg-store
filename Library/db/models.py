from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, CheckConstraint, ForeignKey, TIMESTAMP
from sqlalchemy.dialects.postgresql import ARRAY
from config import MAX_DATA, MIN_DATA
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, Mapped

Base = declarative_base()


class Book(Base):
    __tablename__ = "books"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    title = Column(String, nullable=False, unique=True)
    author = Column(String)
    publication_year = Column(Integer, nullable=False)
    genre = Column(ARRAY(String), nullable=False)
    description = Column(Text)
    cover_image = Column(String)
    price = Column(Integer, nullable=True, default=0)

    history: Mapped['PriceHistory'] = relationship(back_populates='book', cascade='all, delete-orphan',
                                                   single_parent=True)

    __table_args__ = (
        CheckConstraint(f'publication_year >= {MIN_DATA}', name='min_publication_year'),
        CheckConstraint(f'publication_year <= {MAX_DATA}', name='max_publication_year'),
        CheckConstraint('price >= 0', name='positive_price')

    )


class PriceHistory(Base):
    __tablename__ = "price_history"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    book_id = Column(Integer, ForeignKey('books.id'), nullable=False)
    price = Column(Integer, nullable=False)
    date = Column(TIMESTAMP, nullable=False, default=datetime.now())

    book: Mapped['Book'] = relationship(back_populates='history')

    __table_args__ = (
        CheckConstraint('price >= 0', name='positive_price'),

    )
