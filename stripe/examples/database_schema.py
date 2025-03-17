"""
Example database schemas for storing payment information

This file provides example schemas for storing payment information
in a database. You can adapt these examples to your ORM of choice
(SQLAlchemy, Django ORM, etc.)
"""

"""
Example SQL Schema

CREATE TABLE payments (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL,
    payment_intent_id VARCHAR(255) NOT NULL UNIQUE,
    session_id VARCHAR(255),
    amount INTEGER NOT NULL,
    currency VARCHAR(3) NOT NULL DEFAULT 'sgd',
    payment_status VARCHAR(50) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE refunds (
    id SERIAL PRIMARY KEY,
    payment_id INTEGER REFERENCES payments(id),
    refund_id VARCHAR(255) NOT NULL UNIQUE,
    amount INTEGER NOT NULL,
    status VARCHAR(50) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);
"""

# Example SQLAlchemy models
"""
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

Base = declarative_base()

class Payment(Base):
    __tablename__ = 'payments'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(String(255), nullable=False)
    payment_intent_id = Column(String(255), unique=True, nullable=False)
    session_id = Column(String(255))
    amount = Column(Integer, nullable=False)
    currency = Column(String(3), default='sgd')
    payment_status = Column(String(50), nullable=False)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    refunds = relationship('Refund', back_populates='payment')

class Refund(Base):
    __tablename__ = 'refunds'
    
    id = Column(Integer, primary_key=True)
    payment_id = Column(Integer, ForeignKey('payments.id'))
    refund_id = Column(String(255), unique=True, nullable=False)
    amount = Column(Integer, nullable=False)
    status = Column(String(50), nullable=False)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    payment = relationship('Payment', back_populates='refunds')
"""
