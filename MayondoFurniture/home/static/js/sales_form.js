/**
 * SALES FORM MANAGEMENT - MAYONDO FURNITURE SYSTEM
 * =================================================
 * 
 * This file handles all JavaScript functionality for the sales form:
 * - Dynamic stock validation
 * - Quantity limits based on available stock
 * - Real-time product availability checking
 * - Form submission validation
 * 
 * Clean separation from Django backend - communicates via JSON API
 */

class SalesFormManager {
    constructor() {
        this.stockData = {};
        this.formElements = {
            productName: null,
            productType: null,
            quantity: null,
            unitPrice: null,
            totalSalesAmount: null,
            transportRequired: null,
            form: null
        };
        
        this.init();
    }

    /**
     * Initialize the sales form manager
     */
    async init() {
        console.log(' Initializing Sales Form Manager...');
        
        // Wait for DOM to be ready
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', () => this.setup());
        } else {
            this.setup();
        }
    }

    /**
     * Set up form elements and load stock data
     */
    async setup() {
        try {
            // Find form elements
            this.findFormElements();
            
            // Load stock data from backend
            await this.loadStockData();
            
            // Set up event listeners
            this.setupEventListeners();
            
            // Initial validation
            this.updateQuantityLimits();
            
            console.log(' Sales Form Manager initialized successfully');
        } catch (error) {
            console.error(' Error initializing Sales Form Manager:', error);
        }
    }

    /**
     * Find and cache form elements
     */
    findFormElements() {
        this.formElements = {
            productName: document.querySelector('[name="product_name"]'),
            productType: document.querySelector('[name="product_type"]'),
            quantity: document.querySelector('[name="quantity"]'),
            unitPrice: document.querySelector('[name="unit_price"]'),
            totalSalesAmount: document.querySelector('[name="total_sales_amount"]'),
            transportRequired: document.querySelector('[name="transport_required"]'),
            form: document.querySelector('form.crispy-form')
        };

        // Validate that we found all required elements
        const missing = Object.entries(this.formElements)
            .filter(([key, element]) => !element)
            .map(([key]) => key);

        if (missing.length > 0) {
            throw new Error(`Missing form elements: ${missing.join(', ')}`);
        }
    }

    /**
     * Load stock data from the backend API
     */
    async loadStockData() {
        try {
            // Check if we have a global stockData variable (fallback)
            if (typeof window.stockData !== 'undefined') {
                this.stockData = window.stockData;
                console.log(' Loaded stock data from global variable');
                return;
            }

            // Try to load from API endpoint
            const response = await fetch('/api/stock-data/');
            if (response.ok) {
                const data = await response.json();
                this.stockData = data.stock_data || {};
                console.log(' Loaded stock data from API');
            } else {
                throw new Error(`API request failed: ${response.status}`);
            }
        } catch (error) {
            console.warn(' Could not load stock data from API, using empty data:', error);
            this.stockData = {};
        }
    }

    /**
     * Set up event listeners for form interactions
     */
    setupEventListeners() {
        const { productName, productType, quantity, unitPrice } = this.formElements;

        // Product selection changes
        if (productName) {
            productName.addEventListener('change', () => this.updateQuantityLimits());
        }

        if (productType) {
            productType.addEventListener('change', () => this.updateQuantityLimits());
        }

        // Quantity input validation and calculation
        if (quantity) {
            quantity.addEventListener('input', () => {
                this.validateQuantityInput();
                this.calculateTotal();
            });
            quantity.addEventListener('blur', () => {
                this.validateQuantityInput();
                this.calculateTotal();
            });
        }

        // Unit price input and calculation
        if (unitPrice) {
            unitPrice.addEventListener('input', () => this.calculateTotal());
            unitPrice.addEventListener('blur', () => this.calculateTotal());
        }

        // Transport required checkbox
        if (this.formElements.transportRequired) {
            this.formElements.transportRequired.addEventListener('change', () => this.calculateTotal());
        }

        // Form submission validation
        if (this.formElements.form) {
            this.formElements.form.addEventListener('submit', (e) => this.validateFormSubmission(e));
        }
    }

    /**
     * Update quantity limits based on selected product
     */
    updateQuantityLimits() {
        const { productName, productType, quantity } = this.formElements;
        
        if (!productName || !productType || !quantity) {
            console.warn(' Form elements not found for quantity validation');
            return;
        }

        const selectedProduct = productName.value;
        const selectedType = productType.value;

        // Clear previous help text
        this.clearHelpText();

        if (selectedProduct && selectedType) {
            const stockKey = `${selectedProduct}-${selectedType}`;
            const availableStock = this.stockData[stockKey];

            if (availableStock !== undefined && availableStock > 0) {
                this.setQuantityLimits(availableStock);
                this.showStockInfo(availableStock, 'available');
            } else {
                this.setQuantityLimits(0);
                this.showStockInfo(0, 'unavailable');
            }
        } else {
            // No product selected, reset limits
            this.resetQuantityField();
        }
    }

    /**
     * Set quantity field limits and attributes
     */
    setQuantityLimits(maxStock) {
        const { quantity } = this.formElements;
        
        quantity.setAttribute('max', maxStock.toString());
        quantity.setAttribute('title', `Maximum available: ${maxStock} units`);
        
        // Validate current value against new limit
        const currentValue = parseInt(quantity.value) || 0;
        if (currentValue > maxStock) {
            quantity.value = maxStock > 0 ? maxStock.toString() : '';
        }
    }

    /**
     * Show stock availability information
     */
    showStockInfo(stockAmount, status) {
        const { quantity } = this.formElements;
        const container = quantity.parentNode;
        
        const helpText = document.createElement('small');
        helpText.className = 'stock-help-text font-medium mt-1 block';
        
        if (status === 'available') {
            helpText.className += ' text-green-600';
            helpText.textContent = ` Available in stock: ${stockAmount} units`;
        } else {
            helpText.className += ' text-red-600';
            helpText.textContent = ' This product combination is not available in stock';
        }
        
        container.appendChild(helpText);
    }

    /**
     * Clear existing help text
     */
    clearHelpText() {
        const existingHelp = document.querySelectorAll('.stock-help-text');
        existingHelp.forEach(element => element.remove());
    }

    /**
     * Reset quantity field to default state
     */
    resetQuantityField() {
        const { quantity } = this.formElements;
        quantity.removeAttribute('max');
        quantity.removeAttribute('title');
        this.clearHelpText();
    }

    /**
     * Validate quantity input in real-time
     */
    validateQuantityInput() {
        const { quantity } = this.formElements;
        const value = parseInt(quantity.value) || 0;
        const max = parseInt(quantity.getAttribute('max')) || 0;

        if (value > max && max > 0) {
            quantity.value = max.toString();
            this.showValidationMessage(`Quantity cannot exceed ${max} units`, 'warning');
        } else if (value < 1 && quantity.value !== '') {
            quantity.value = '1';
            this.showValidationMessage('Quantity must be at least 1', 'warning');
        }
    }

    /**
     * Validate form before submission
     */
    validateFormSubmission(event) {
        const { productName, productType, quantity } = this.formElements;
        
        const selectedProduct = productName?.value;
        const selectedType = productType?.value;
        const quantityValue = parseInt(quantity?.value) || 0;

        // Check if product combination is available
        if (selectedProduct && selectedType) {
            const stockKey = `${selectedProduct}-${selectedType}`;
            const availableStock = this.stockData[stockKey] || 0;

            if (availableStock <= 0) {
                event.preventDefault();
                this.showValidationMessage(
                    ` ${selectedProduct} (${selectedType}) is not available in stock`,
                    'error'
                );
                return false;
            }

            if (quantityValue > availableStock) {
                event.preventDefault();
                this.showValidationMessage(
                    ` Cannot sell ${quantityValue} units. Only ${availableStock} units available`,
                    'error'
                );
                return false;
            }
        }

        return true;
    }

    /**
     * Show validation message to user
     */
    showValidationMessage(message, type = 'info') {
        // Remove existing messages
        const existing = document.querySelectorAll('.sales-form-message');
        existing.forEach(el => el.remove());

        // Create new message
        const messageEl = document.createElement('div');
        messageEl.className = `sales-form-message p-3 mb-4 rounded-lg ${this.getMessageClasses(type)}`;
        messageEl.textContent = message;

        // Insert at top of form
        const form = this.formElements.form;
        if (form) {
            form.insertBefore(messageEl, form.firstChild);
            
            // Auto-remove after 5 seconds
            setTimeout(() => {
                if (messageEl.parentNode) {
                    messageEl.remove();
                }
            }, 5000);
        }
    }

    /**
     * Get CSS classes for message types
     */
    getMessageClasses(type) {
        const classes = {
            'error': 'bg-red-100 border border-red-400 text-red-700',
            'warning': 'bg-yellow-100 border border-yellow-400 text-yellow-700',
            'success': 'bg-green-100 border border-green-400 text-green-700',
            'info': 'bg-blue-100 border border-blue-400 text-blue-700'
        };
        return classes[type] || classes['info'];
    }

    /**
     * Calculate total sales amount automatically
     */
    calculateTotal() {
        const { quantity, unitPrice, totalSalesAmount, transportRequired } = this.formElements;
        
        if (!quantity || !unitPrice || !totalSalesAmount) {
            console.warn(' Some form elements not found for calculation');
            return;
        }

        const quantityValue = parseFloat(quantity.value) || 0;
        const unitPriceValue = parseFloat(unitPrice.value) || 0;
        const isTransportRequired = transportRequired ? transportRequired.checked : false;
        
        console.log(` Calculating total: ${quantityValue} × ${unitPriceValue} (transport: ${isTransportRequired})`);
        
        if (quantityValue > 0 && unitPriceValue > 0) {
            // Calculate base amount
            let total = quantityValue * unitPriceValue;
            
            // Add 5% transport fee if required
            if (isTransportRequired) {
                const transportFee = total * 0.05;
                total += transportFee;
                console.log(` Transport fee added: ${transportFee.toFixed(2)} (5%)`);
            }
            
            totalSalesAmount.value = total.toFixed(2);
            
            console.log(` Final total: ${total.toFixed(2)}`);
            
            // Visual feedback for successful calculation
            totalSalesAmount.style.backgroundColor = '#d4edda';
            setTimeout(() => {
                totalSalesAmount.style.backgroundColor = '';
            }, 1000);
        } else {
            totalSalesAmount.value = '0.00';
            console.log('ℹ️ Setting total to 0.00 (invalid inputs)');
        }
    }

    /**
     * Update stock data (for external calls)
     */
    updateStockData(newStockData) {
        this.stockData = newStockData;
        this.updateQuantityLimits();
        console.log(' Stock data updated');
    }
}

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.salesFormManager = new SalesFormManager();
});

// Export for external access
window.SalesFormManager = SalesFormManager;

// Global function for form widgets to call
function calculateTotal() {
    if (window.salesFormManager) {
        window.salesFormManager.calculateTotal();
    }
}