from app.database import Base
from sqlalchemy import Column, Integer, String, ForeignKey, Date
from sqlalchemy.orm import relationship

class Book(Base):
    __tablename__ = 'books'
    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)
    author = Column(String, nullable=False)
    genre = Column(String, nullable=False)
    page_count = Column(Integer, nullable=False)

    logs = relationship('ReadLog', back_populates='book')

    def __repr__(self):
        return f"<Book(title='{self.title}', author='{self.author}', genre='{self.genre}', page_count={self.page_count})>"

class ReadLog(Base):
    __tablename__ = 'readlogs'
    id = Column(Integer, primary_key=True)
    book_id = Column(Integer, ForeignKey('books.id'), nullable=False)
    status = Column(String, nullable=False)
    rating = Column(Integer, nullable=False)
    read_date = Column(Date, nullable=False)
    read_pages = Column(Integer, nullable=False)

    book = relationship('Book', back_populates='logs')