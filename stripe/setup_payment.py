"""
setup_payment.py
PC Components Store - Stripe Integration

This script creates PC component products in your Stripe account.
"""

import stripe
import os
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

stripe.api_key = os.getenv('STRIPE_SECRET_KEY')

def create_data():
    try:
        # PC Components as Products
        cpu = stripe.Product.create(
            name="AMD Ryzen 5 5600X",
            description="6-core, 12-thread desktop processor",
            images=["https://example.com/cpu.jpg"],
            metadata={
                "category": "cpu",
                "cores": "6",
                "threads": "12"
            }
        )
        
        gpu = stripe.Product.create(
            name="NVIDIA RTX 3070",
            description="High-performance graphics card",
            images=["https://example.com/gpu.jpg"],
            metadata={
                "category": "gpu",
                "memory": "8GB"
            }
        )
        
        # Create prices for products
        stripe.Price.create(
            product=cpu.id,
            unit_amount=29999,  # $299.99
            currency="usd",
            recurring=None  # One-time purchase
        )
        
        stripe.Price.create(
            product=gpu.id,
            unit_amount=59999,  # $599.99
            currency="usd",
            recurring=None  # One-time purchase
        )
        
        print("Products and prices created successfully")
        return True

    except stripe.error.StripeError as e:
        print(f"Error creating products: {e}")
        return False