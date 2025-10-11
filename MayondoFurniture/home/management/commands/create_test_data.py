"""
Test script to demonstrate the new Stock functionality with automatic total cost calculation
and Profit calculation on the dashboard.

This script will:
1. Create sample stock entries with unit_cost to demonstrate auto-calculation
2. Create sample sales to demonstrate profit calculation
3. Show the dashboard with the new profit card

Run this script after starting the Django server to see the new features in action.
"""

from django.core.management.base import BaseCommand
from home.models import Stock, Sale, Product
from django.contrib.auth.models import User
from datetime import date, timedelta
from decimal import Decimal

class Command(BaseCommand):
    help = 'Create sample data to demonstrate new stock and profit functionality'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Creating sample data for testing...'))
        
        # Create sample employees for the sales agent dropdown
        from django.contrib.auth.models import Group
        
        # Create Employee group if it doesn't exist
        employee_group, created = Group.objects.get_or_create(name='Employee')
        
        # Create sample employees
        employees_data = [
            {'username': 'john_mukasa', 'first_name': 'John', 'last_name': 'Mukasa', 'email': 'john@mwf.com'},
            {'username': 'mary_nakato', 'first_name': 'Mary', 'last_name': 'Nakato', 'email': 'mary@mwf.com'},
            {'username': 'david_ssemakula', 'first_name': 'David', 'last_name': 'Ssemakula', 'email': 'david@mwf.com'},
        ]
        
        for emp_data in employees_data:
            employee, created = User.objects.get_or_create(
                username=emp_data['username'],
                defaults=emp_data
            )
            if created:
                employee.set_password('password123')
                employee.save()
                # Add to Employee group
                employee.groups.add(employee_group)
                self.stdout.write(f'Created employee: {employee.first_name} {employee.last_name}')
        
        # Use first employee as default sales agent
        default_agent = User.objects.filter(groups__name="Employee").first()
        if not default_agent:
            # Fallback: create a test agent
            default_agent, created = User.objects.get_or_create(
                username='test_agent',
                defaults={'email': 'test@example.com', 'first_name': 'Test', 'last_name': 'Agent'}
            )
            if created:
                default_agent.set_password('testpassword')
                default_agent.save()
                default_agent.groups.add(employee_group)
        
        # Create sample products if they don't exist
        products_to_create = [
            ('Timber', 'Wood'),
            ('Sofa', 'Furniture'),
            ('Tables', 'Furniture')
        ]
        
        for name, product_type in products_to_create:
            product, created = Product.objects.get_or_create(
                name=name,
                product_type=product_type,
                defaults={'description': f'Sample {name} for testing'}
            )
            if created:
                self.stdout.write(f'Created product: {product}')
        
        # Create sample stock entries with the new unit_cost field
        stock_entries = [
            {
                'product_name': 'Timber',
                'product_type': 'Wood',
                'quantity': 100,
                'unit_cost': Decimal('5000.00'),  # UGX 5,000 per piece
                'supplier_name': 'Mbawo Timberworks',
                'origin': 'Western',
                'date': date.today() - timedelta(days=10)
            },
            {
                'product_name': 'Sofa',
                'product_type': 'Furniture',
                'quantity': 20,
                'unit_cost': Decimal('150000.00'),  # UGX 150,000 per sofa
                'supplier_name': 'Rosewood Timbers',
                'origin': 'Central',
                'date': date.today() - timedelta(days=5)
            },
            {
                'product_name': 'Tables',
                'product_type': 'Furniture',
                'quantity': 15,
                'unit_cost': Decimal('80000.00'),  # UGX 80,000 per table
                'supplier_name': 'Matongo WoodWorks',
                'origin': 'Eastern',
                'date': date.today() - timedelta(days=3)
            }
        ]
        
        for stock_data in stock_entries:
            stock, created = Stock.objects.get_or_create(
                product_name=stock_data['product_name'],
                product_type=stock_data['product_type'],
                date=stock_data['date'],
                defaults=stock_data
            )
            if created:
                self.stdout.write(f'Created stock: {stock.product_name} - Qty: {stock.quantity}, Unit Cost: {stock.unit_cost}, Total Cost: {stock.total_cost}')
        
        # Create sample sales to demonstrate profit calculation
        sales_entries = [
            {
                'customer_name': 'John Mukasa',
                'product_name': 'Timber',
                'product_type': 'Wood',
                'quantity': 50,  # Sold 50 pieces
                'unit_price': Decimal('8000.00'),  # Same as stock price
                'date': date.today() - timedelta(days=2),
                'payment_type': 'Cash',
                'sales_agent': default_agent.username,
                'transport_required': False
            },
            {
                'customer_name': 'Mary Nakato',
                'product_name': 'Sofa',
                'product_type': 'Furniture',
                'quantity': 3,  # Sold 3 sofas
                'unit_price': Decimal('200000.00'),  # Same as stock price
                'date': date.today() - timedelta(days=1),
                'payment_type': 'Bank Overdraft',
                'sales_agent': default_agent.username,
                'transport_required': True  # This will add 5% transport fee
            },
            {
                'customer_name': 'David Ssemakula',
                'product_name': 'Tables',
                'product_type': 'Furniture',
                'quantity': 5,  # Sold 5 tables
                'unit_price': Decimal('120000.00'),  # Same as stock price
                'date': date.today(),
                'payment_type': 'Cheque',
                'sales_agent': default_agent.username,
                'transport_required': False
            }
        ]
        
        for sale_data in sales_entries:
            sale, created = Sale.objects.get_or_create(
                customer_name=sale_data['customer_name'],
                product_name=sale_data['product_name'],
                product_type=sale_data['product_type'],
                date=sale_data['date'],
                defaults=sale_data
            )
            if created:
                self.stdout.write(f'Created sale: {sale.customer_name} - {sale.product_name} x{sale.quantity} = {sale.total_sales_amount}')
        
        self.stdout.write(self.style.SUCCESS('\nSample data created successfully!'))
        self.stdout.write(self.style.WARNING('\nProfit Calculation Summary:'))
        
        # Calculate expected profit for verification
        timber_profit = (8000 - 5000) * 50  # UGX 150,000
        sofa_revenue = 200000 * 3 * 1.05  # With 5% transport fee
        sofa_profit = sofa_revenue - (150000 * 3)  # Revenue - Cost
        table_profit = (120000 - 80000) * 5  # UGX 200,000
        
        total_expected_profit = timber_profit + sofa_profit + table_profit
        
        self.stdout.write(f'Expected Timber Profit: UGX {timber_profit:,}')
        self.stdout.write(f'Expected Sofa Profit: UGX {sofa_profit:,}')
        self.stdout.write(f'Expected Table Profit: UGX {table_profit:,}')
        self.stdout.write(f'Total Expected Profit: UGX {total_expected_profit:,}')
        
        self.stdout.write(self.style.SUCCESS('\nYou can now:'))
        self.stdout.write('1. Visit http://127.0.0.1:8000/ to see the dashboard with the new Profit card')
        self.stdout.write('2. Go to Add Stock to test the automatic total cost calculation')
        self.stdout.write('3. See how unit_cost × quantity = total_cost automatically')