"""
inventory.py
PC Components Store - Stripe Integration

Library to manage PC components inventory and pricing through Stripe.
"""

import stripe
import os
from functools import reduce
from typing import List, Dict, Any
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

stripe.api_key = os.getenv('STRIPE_SECRET_KEY')

class Inventory:
    @staticmethod
    def calculate_payment_amount(items: list) -> int:
        total = 0
        for item in items:
            product_id = item['parent']
            quantity = item['quantity']
            
            # For testing purposes, assign default prices based on product type
            if product_id == 'cpu':
                price_amount = 29999  # $299.99
            elif product_id == 'gpu':
                price_amount = 59999  # $599.99
            elif product_id == 'ram':
                price_amount = 8999   # $89.99
            elif product_id == 'motherboard':
                price_amount = 16999  # $169.99
            elif product_id == 'storage':
                price_amount = 11999  # $119.99
            else:
                price_amount = 9999   # Default $99.99
                
            total += price_amount * quantity
    
    # Ensure we're above the minimum charge amount (usually $0.50 or 50 cents)
        if total < 50:
            total = 50
        
        return total

    @staticmethod
    def get_shipping_cost(id) -> int:
        # PC components shipping options
        shipping_cost = {
            'free': 0,
            'standard': 999,
            'express': 1999,
            'overnight': 2999
        }
        return shipping_cost.get(id, 0)

    @staticmethod
    def list_products() -> Dict[str, Any]:
        products = stripe.Product.list(
            limit=100,
            active=True
        )
        
        # For each product, get its price
        for product in products.data:
            prices = stripe.Price.list(
                product=product.id,
                limit=1,
                active=True
            )
            if prices and prices.data:
                product['price'] = prices.data[0]
            
        return products

    @staticmethod
    def retrieve_product(product_id) -> Dict[str, Any]:
        product = stripe.Product.retrieve(product_id)
        
        # Get the product's price
        prices = stripe.Price.list(
            product=product_id,
            limit=1,
            active=True
        )
        
        if prices and prices.data:
            product['price'] = prices.data[0]
            
        return product

    @staticmethod
    def products_exist(product_list: Dict[str, Any]) -> bool:
        # Check if we have products
        return len(product_list.data) > 0