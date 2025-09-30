# Mayondo Furniture Management System (MWF)

A comprehensive Django web application for managing furniture business operations including sales, inventory, and reporting.

## 🏢 Business Overview

**Mayondo Wood & Furniture** is a furniture business management system designed to streamline operations for:
- Sales tracking and management
- Inventory control and stock management  
- Financial reporting and analytics
- User management with role-based access
- Real-time business intelligence dashboard

## 🚀 Features

### 📊 Dashboard
- **Real-time Statistics**: Live revenue, sales count, stock levels, out-of-stock alerts
- **Recent Sales Table**: Display of latest sales with product ID, amounts in UGX currency
- **Interactive Navigation**: Dropdown menus for easy access to all features
- **Search Functionality**: Quick search across dashboard data
- **Notifications System**: Real-time alerts and activity feed

### 👥 User Management
- **Role-based Access Control**: Manager and Employee roles with different permissions
- **Secure Authentication**: Login system with role verification
- **User Creation**: Managers can add new employees to the system

### 💰 Sales Management
- **Create Sales**: Add new sales records with customer details, payment methods
- **View All Sales**: Complete sales history with filtering and search
- **Edit Sales**: Modify existing sales records
- **Delete Sales**: Remove sales records with confirmation prompts
- **Sales Reports**: Generate detailed sales analytics and reports

### 📦 Inventory Management  
- **Stock Addition**: Add new inventory items with supplier information
- **Stock Tracking**: Monitor quantities, prices (unit and total costs)
- **Stock Reports**: Inventory analytics and low-stock alerts
- **CRUD Operations**: Full create, read, update, delete functionality

### 📈 Reporting System
- **Sales Reports**: Revenue analysis, sales trends, agent performance
- **Stock Reports**: Inventory levels, product categories, supplier tracking
- **Custom Reports**: Generate reports based on date ranges and criteria
- **Export Options**: Various report formats for business analysis

## 🛠 Technical Stack

### Backend
- **Framework**: Django 5.2.6
- **Database**: SQLite3 (development) / PostgreSQL (production ready)
- **Authentication**: Django's built-in user authentication with custom groups
- **Forms**: Django ModelForms with crispy-forms for professional styling

### Frontend
- **CSS Framework**: Tailwind CSS for modern, responsive design
- **Icons**: FontAwesome 6.4.0 for professional iconography
- **JavaScript**: Vanilla JS for interactive components (dropdowns, modals)
- **UI Components**: Custom dropdown navigation, search functionality

### Key Libraries
- **django-crispy-forms**: Professional form rendering
- **crispy-tailwind**: Tailwind CSS integration for forms
- **Chart.js**: Data visualization and charts
- **FontAwesome**: Icon system

## 📁 Project Structure

```
MayondoFurniture/
├── MayondoFurniture/          # Main project directory
│   ├── settings.py            # Django settings and configuration
│   ├── urls.py               # Main URL routing with comprehensive comments
│   ├── wsgi.py               # WSGI configuration for deployment
│   └── asgi.py               # ASGI configuration for async support
├── home/                      # Main application directory
│   ├── models.py             # Database models (Sale, Stock, Notification)
│   ├── views.py              # Business logic and view functions
│   ├── forms.py              # Django forms with crispy styling
│   ├── admin.py              # Django admin configuration
│   ├── search.py             # Search functionality
│   ├── signals.py            # Django signals for notifications
│   ├── templates/            # HTML templates
│   │   ├── base.html         # Master template with navigation
│   │   ├── dashboard.html    # Main dashboard interface
│   │   ├── login.html        # User authentication
│   │   ├── sales/            # Sales-related templates
│   │   ├── stock/            # Inventory templates
│   │   └── reports/          # Report templates
│   ├── static/               # Static files (CSS, images, JS)
│   └── migrations/           # Database migrations
├── db.sqlite3                # Development database
├── manage.py                 # Django management script
└── README.md                 # This documentation file
```

## 🎨 Design System

### Color Scheme
- **Primary**: `#005f66` (cordes-blue) - Headers, primary buttons
- **Secondary**: `#007b83` (cordes-dark) - Navigation, accents  
- **Background**: Gray-50 for clean, professional appearance
- **Text**: Gray-900 for high contrast and readability

### Typography
- **Headers**: Bold, hierarchical sizing (text-2xl, text-lg)
- **Body Text**: Clean, readable fonts with proper contrast
- **UI Elements**: Consistent sizing and spacing

### Layout
- **Responsive Grid**: Mobile-first design with Tailwind's grid system
- **Navigation**: Fixed sidebar on desktop, collapsible on mobile
- **Cards**: Elevated cards with shadows for content grouping
- **Forms**: Professional styling with crispy-forms integration

## 🔒 Security Features

- **Authentication Required**: All main features require user login
- **Role-based Access**: Different permissions for Managers vs Employees
- **CSRF Protection**: Built-in Django CSRF protection for all forms
- **Direct Access Prevention**: Security decorators prevent unauthorized URL access
- **Session Management**: Secure user sessions with proper logout handling

## 💱 Currency & Localization

- **Currency**: Uganda Shillings (UGX) - formatted without decimals
- **Date Format**: International date formatting
- **Number Format**: Comma-separated thousands for large numbers
- **Regional**: Designed for Uganda-based furniture business operations

## 🚀 Getting Started

### Prerequisites
- Python 3.8+
- Django 5.2.6
- Virtual environment (recommended)

### Installation

1. **Clone the Repository**
   ```bash
   git clone <repository-url>
   cd MayondoFurniture
   ```

2. **Create Virtual Environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   venv\Scripts\activate     # Windows
   ```

3. **Install Dependencies**
   ```bash
   pip install django==5.2.6
   pip install django-crispy-forms
   pip install crispy-tailwind
   ```

4. **Database Setup**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

5. **Create Superuser**
   ```bash
   python manage.py createsuperuser
   ```

6. **Create User Groups**
   ```bash
   python manage.py shell
   >>> from django.contrib.auth.models import Group
   >>> Group.objects.create(name='Manager')
   >>> Group.objects.create(name='Employee')
   >>> exit()
   ```

7. **Run Development Server**
   ```bash
   python manage.py runserver
   ```

8. **Access the Application**
   - Open browser to `http://127.0.0.1:8000/`
   - Login with superuser credentials
   - Navigate to dashboard to begin using the system

## 👤 User Roles

### Manager
- Full system access
- Can add new users
- Access to all sales and stock operations
- Complete reporting capabilities
- User management functions

### Employee  
- Sales management (add, view, edit sales)
- Stock management (add, view inventory)
- Basic reporting access
- Personal notifications

## 📱 Navigation

### Header Navigation (Global)
- **Dashboard**: Quick access to main dashboard
- **Stock Dropdown**: Add Stock, All Stock, Stock Reports
- **Sales Dropdown**: Add Sale, All Sales, Sales Reports  
- **Reports Dropdown**: Generate Reports, All Report Types

### Sidebar Navigation (Dashboard)
- **Role-specific Menus**: Different options for Managers vs Employees
- **Dropdown Menus**: Organized by functional areas
- **Visual Icons**: FontAwesome icons for intuitive navigation

## 📊 Data Models

### Sale Model
- Product identification and customer details
- Quantity and pricing information
- Payment method and logistics (transport)
- Sales agent tracking
- Date/time stamps

### Stock Model  
- Product categories (Timber, Sofa, Tables, Cupboards, Drawer, Poles)
- Supplier information and origin tracking
- Pricing: unit price and total cost
- Inventory quantity management

### Notification Model
- User-specific notifications
- Activity types and read status
- Timestamp tracking for chronological display

## 🔧 Customization

The system is designed to be easily customizable:

- **Colors**: Modify Tailwind config in base.html for different brand colors
- **Product Categories**: Update CUSTOMER_CHOICES in models.py
- **Payment Methods**: Modify PAYMENT_CHOICES for different payment options
- **Currency**: Change UGX references for different currency systems
- **Business Logic**: Extend views.py for additional functionality

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Add comprehensive comments to new code
4. Commit changes (`git commit -m 'Add some AmazingFeature'`)
5. Push to branch (`git push origin feature/AmazingFeature`)
6. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 👨‍💻 Developer Notes

### Code Organization
- **Views**: Each view function has comprehensive docstrings explaining purpose and functionality
- **Models**: Field-level comments explain business logic and relationships
- **Templates**: HTML comments explain section purposes and key features
- **URLs**: Organized with clear section headers and explanatory comments

### Best Practices Implemented
- **Django Conventions**: Following Django best practices for MVT architecture
- **Security First**: CSRF protection, user authentication, role-based access
- **Responsive Design**: Mobile-first approach with Tailwind CSS
- **Code Documentation**: Extensive comments for maintainability
- **Error Handling**: Proper exception handling and user-friendly error messages

---

**Mayondo Wood & Furniture Management System** - Streamlining furniture business operations with modern web technology. 🪑✨