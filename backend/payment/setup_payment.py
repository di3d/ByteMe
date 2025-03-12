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
        products = [
            # CPUs
            {
                'name': 'AMD Ryzen 7 5800X',
                'description': '8-Core CPU, 3.8GHz base clock, 4.7GHz boost',
                'metadata': {
                    'category': 'cpu',
                    'brand': 'AMD',
                    'cores': '8-Core'
                }
            },
            {
                'name': 'Intel Core i7-12700K',
                'description': '12-Core CPU (8P+4E), up to 5.0GHz',
                'metadata': {
                    'category': 'cpu',
                    'brand': 'Intel',
                    'cores': '12-Core'
                }
            },
            
            # GPUs
            {
                'name': 'NVIDIA RTX 3070',
                'description': '8GB GDDR6 Graphics Card',
                'metadata': {
                    'category': 'gpu',
                    'brand': 'NVIDIA',
                    'memory': '8GB GDDR6'
                }
            },
            {
                'name': 'AMD RX 6700 XT',
                'description': '12GB GDDR6 Graphics Card',
                'metadata': {
                    'category': 'gpu',
                    'brand': 'AMD',
                    'memory': '12GB GDDR6'
                }
            },
            
            # RAM
            {
                'name': 'Corsair Vengeance 16GB DDR4',
                'description': '16GB (2x8GB) DDR4-3200 Memory',
                'metadata': {
                    'category': 'ram',
                    'capacity': '16GB',
                    'speed': '3200MHz'
                }
            },
            {
                'name': 'G.Skill Trident Z 32GB DDR4',
                'description': '32GB (2x16GB) DDR4-3600 Memory',
                'metadata': {
                    'category': 'ram',
                    'capacity': '32GB',
                    'speed': '3600MHz'
                }
            },
            
            # Motherboards
            {
                'name': 'MSI B550 Gaming Edge',
                'description': 'ATX Motherboard for AMD Ryzen CPUs',
                'metadata': {
                    'category': 'motherboard',
                    'chipset': 'B550',
                    'form_factor': 'ATX'
                }
            },
            {
                'name': 'ASUS ROG Z690 Hero',
                'description': 'ATX Motherboard for Intel 12th Gen CPUs',
                'metadata': {
                    'category': 'motherboard',
                    'chipset': 'Z690',
                    'form_factor': 'ATX'
                }
            },
            
            # Storage
            {
                'name': 'Samsung 970 EVO Plus 1TB',
                'description': '1TB NVMe SSD, up to 3500MB/s read',
                'metadata': {
                    'category': 'storage',
                    'type': 'NVMe SSD',
                    'capacity': '1TB'
                }
            },
            {
                'name': 'Seagate Barracuda 4TB',
                'description': '4TB 5400RPM HDD',
                'metadata': {
                    'category': 'storage',
                    'type': 'HDD',
                    'capacity': '4TB'
                }
            }
        ]

        created_products = []
        
        # Create products and their associated prices
        for product_data in products:
            # Set a default price based on the category
            price_amount = 0
            if product_data['metadata']['category'] == 'cpu':
                if 'AMD' in product_data['name']:
                    price_amount = 29999  # $299.99
                else:
                    price_amount = 34999  # $349.99
            elif product_data['metadata']['category'] == 'gpu':
                if 'NVIDIA' in product_data['name']:
                    price_amount = 59999  # $599.99
                else:
                    price_amount = 49999  # $499.99
            elif product_data['metadata']['category'] == 'ram':
                if '16GB' in product_data['name']:
                    price_amount = 8999   # $89.99
                else:
                    price_amount = 14999  # $149.99
            elif product_data['metadata']['category'] == 'motherboard':
                if 'B550' in product_data['name']:
                    price_amount = 16999  # $169.99
                else:
                    price_amount = 24999  # $249.99
            elif product_data['metadata']['category'] == 'storage':
                if 'SSD' in product_data['metadata']['type']:
                    price_amount = 11999  # $119.99
                else:
                    price_amount = 7999   # $79.99
            
            # Create the product
            product = stripe.Product.create(**product_data)
            
            # Create a price for the product
            stripe.Price.create(
                product=product.id,
                unit_amount=price_amount,  # amount in cents
                currency='usd',
                metadata={
                    'product_id': product.id
                }
            )
            
            created_products.append(product)
        
        print(f"Successfully created {len(created_products)} PC component products in Stripe")
        return created_products

    except stripe.error.StripeError as e:
        print(f'Error creating products: {e}')
        return None