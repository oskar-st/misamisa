/**
 * CartManager - Optimistic cart updates with batched operations
 * 
 * Features:
 * - Optimistic UI updates (instant feedback)
 * - Debounced batching (reduces server requests)
 * - Conflict resolution (handles stock adjustments)
 * - AbortController support (cancels stale requests)
 */

class CartManager {
    constructor() {
        this.operationQueue = [];
        this.isProcessing = false;
        this.abortController = null;
        this.clientRev = 0;
        this.flushTimeout = null;
        
        // Configuration
        this.config = {
            debounceMs: 400,
            batchEndpoint: '/sklep/api/cart/batch/',
            maxRetries: 3
        };
        
        this.initializeEventHandlers();
    }
    
    /**
     * Initialize event handlers for cart interactions
     */
    initializeEventHandlers() {
        // Listen for quantity input changes with debouncing
        document.addEventListener('input', (e) => {
            if (e.target.matches('[id^="cart-qty-"]')) {
                const productId = this.extractProductId(e.target.id);
                const quantity = parseInt(e.target.value) || 0;
                this.updateQuantity(productId, quantity);
            }
        });
        
        // Listen for remove buttons
        document.addEventListener('click', (e) => {
            if (e.target.matches('[data-cart-remove]')) {
                e.preventDefault();
                const productId = e.target.dataset.cartRemove;
                this.removeItem(productId);
            }
        });
    }
    
    /**
     * Update item quantity with optimistic UI
     * @param {string|number} productId 
     * @param {number} quantity 
     */
    updateQuantity(productId, quantity) {
        productId = String(productId);
        quantity = Math.max(0, parseInt(quantity) || 0);
        
        // 1. Optimistic UI update
        this.updateUIImmediately(productId, quantity);
        
        // 2. Queue operation
        this.queueOperation({
            product_id: productId,
            quantity: quantity,
            action: 'update'
        });
        
        // 3. Schedule batch send
        this.scheduleFlush();
    }
    
    /**
     * Remove item from cart
     * @param {string|number} productId 
     */
    removeItem(productId) {
        productId = String(productId);
        
        // 1. Optimistic UI update
        this.updateUIImmediately(productId, 0);
        
        // 2. Queue operation
        this.queueOperation({
            product_id: productId,
            action: 'remove'
        });
        
        // 3. Schedule batch send
        this.scheduleFlush();
    }
    
    /**
     * Queue an operation, merging with existing operations for the same product
     * @param {Object} operation 
     */
    queueOperation(operation) {
        const productId = operation.product_id;
        
        // Remove any existing operation for this product (latest wins)
        this.operationQueue = this.operationQueue.filter(op => op.product_id !== productId);
        
        // Add new operation
        this.operationQueue.push(operation);
    }
    
    /**
     * Schedule a flush with debouncing
     */
    scheduleFlush() {
        // Clear existing timeout
        if (this.flushTimeout) {
            clearTimeout(this.flushTimeout);
        }
        
        // Schedule new flush
        this.flushTimeout = setTimeout(() => {
            this.flush();
        }, this.config.debounceMs);
    }
    
    /**
     * Send batched operations to server
     */
    async flush() {
        if (!this.operationQueue.length || this.isProcessing) {
            return;
        }
        
        // Cancel any in-flight request
        if (this.abortController) {
            this.abortController.abort();
        }
        this.abortController = new AbortController();
        
        const operations = [...this.operationQueue];
        this.operationQueue = [];
        this.isProcessing = true;
        
        try {
            const response = await fetch(this.config.batchEndpoint, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCsrfToken()
                },
                body: JSON.stringify({
                    ops: operations,
                    client_rev: this.clientRev
                }),
                signal: this.abortController.signal
            });
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            
            const data = await response.json();
            
            if (data.success) {
                this.clientRev = data.server_rev;
                this.reconcileUI(data);
            } else {
                console.error('Cart batch update failed:', data.error);
                this.showNotification('Failed to update cart. Please refresh the page.', 'error');
            }
            
        } catch (error) {
            if (error.name !== 'AbortError') {
                console.error('Cart sync failed:', error);
                this.showNotification('Connection error. Your changes may not be saved.', 'warning');
                
                // Re-queue operations for retry (simple strategy)
                this.operationQueue = [...operations, ...this.operationQueue];
                this.scheduleFlush();
            }
        } finally {
            this.isProcessing = false;
        }
    }
    
    /**
     * Update UI immediately for optimistic feedback
     * @param {string} productId 
     * @param {number} quantity 
     */
    updateUIImmediately(productId, quantity) {
        // Update quantity input
        const input = document.getElementById(`cart-qty-${productId}`);
        if (input && parseInt(input.value) !== quantity) {
            input.value = quantity;
        }
        
        // Update subtotal (estimate based on current price)
        const subtotalEl = document.querySelector(`.item-subtotal[data-product-id="${productId}"]`);
        if (subtotalEl && quantity > 0) {
            const price = parseFloat(subtotalEl.dataset.price || 0);
            if (price) {
                subtotalEl.textContent = (price * quantity).toFixed(2) + ' zł';
            }
        }
        
        // Remove row if quantity is 0
        if (quantity === 0) {
            const row = document.querySelector(`tr[data-product-id="${productId}"], .cart-item[data-product-id="${productId}"]`);
            if (row) {
                row.style.opacity = '0.5';
                setTimeout(() => {
                    row.remove();
                    this.checkEmptyCart();
                }, 200);
            }
        }
        
        // Update cart badge and totals (estimate)
        this.updateCartSummary();
    }
    
    /**
     * Reconcile UI with server response
     * @param {Object} serverData 
     */
    reconcileUI(serverData) {
        // Handle notices (stock adjustments, errors, etc.)
        if (serverData.notices && serverData.notices.length > 0) {
            serverData.notices.forEach(notice => {
                this.handleNotice(notice);
            });
        }
        
        // Update totals with authoritative server values
        this.updateCartTotals(serverData.total, serverData.cart_count);
        
        // Update individual item subtotals if they were adjusted
        if (serverData.cart && serverData.cart.items) {
            serverData.cart.items.forEach(item => {
                const subtotalEl = document.querySelector(`.item-subtotal[data-product-id="${item.product_id}"]`);
                if (subtotalEl) {
                    subtotalEl.textContent = item.subtotal.toFixed(2) + ' zł';
                }
                
                // Update quantity if server made adjustments
                const input = document.getElementById(`cart-qty-${item.product_id}`);
                if (input && parseInt(input.value) !== item.quantity) {
                    input.value = item.quantity;
                }
            });
        }
    }
    
    /**
     * Handle server notices (stock adjustments, errors, etc.)
     * @param {Object} notice 
     */
    handleNotice(notice) {
        let message = notice.message;
        let type = 'info';
        
        switch (notice.type) {
            case 'stock_adjustment':
                type = 'warning';
                // Update the input to reflect the adjusted quantity
                if (notice.product_id && notice.adjusted_quantity !== undefined) {
                    const input = document.getElementById(`cart-qty-${notice.product_id}`);
                    if (input) {
                        input.value = notice.adjusted_quantity;
                    }
                }
                break;
            case 'error':
                type = 'error';
                break;
            case 'removed':
                type = 'info';
                break;
        }
        
        this.showNotification(message, type);
    }
    
    /**
     * Update cart summary (badge, totals) with estimated values
     */
    updateCartSummary() {
        let totalItems = 0;
        let estimatedTotal = 0;
        
        // Count items and estimate total from DOM
        document.querySelectorAll('[id^="cart-qty-"]').forEach(input => {
            const quantity = parseInt(input.value) || 0;
            totalItems += quantity;
            
            const productId = this.extractProductId(input.id);
            const subtotalEl = document.querySelector(`.item-subtotal[data-product-id="${productId}"]`);
            if (subtotalEl) {
                const price = parseFloat(subtotalEl.dataset.price || 0);
                estimatedTotal += price * quantity;
            }
        });
        
        // Update cart badge
        const cartBadge = document.querySelector('.cart-badge');
        if (cartBadge) {
            cartBadge.textContent = totalItems;
            cartBadge.style.display = totalItems > 0 ? 'flex' : 'none';
        }
        
        // Update total (if available)
        const cartTotalEl = document.getElementById('cart-total');
        if (cartTotalEl && estimatedTotal > 0) {
            cartTotalEl.textContent = estimatedTotal.toFixed(2);
        }
    }
    
    /**
     * Update cart totals with authoritative server values
     * @param {number} total 
     * @param {number} count 
     */
    updateCartTotals(total, count) {
        // Update cart badge
        const cartBadge = document.querySelector('.cart-badge');
        if (cartBadge) {
            cartBadge.textContent = count;
            cartBadge.style.display = count > 0 ? 'flex' : 'none';
        }
        
        // Update total
        const cartTotalEl = document.getElementById('cart-total');
        if (cartTotalEl) {
            cartTotalEl.textContent = total.toFixed(2);
        }
        
        // Update header cart total
        const headerCartTotal = document.querySelector('.cart-total');
        if (headerCartTotal) {
            headerCartTotal.textContent = total.toFixed(2) + ' zł';
        }
    }
    
    /**
     * Check if cart is empty and handle accordingly
     */
    checkEmptyCart() {
        const cartItems = document.querySelectorAll('[data-product-id]');
        if (cartItems.length === 0) {
            // Cart is empty, could reload page or show empty state
            setTimeout(() => {
                location.reload();
            }, 500);
        }
    }
    
    /**
     * Show notification to user
     * @param {string} message 
     * @param {string} type 
     */
    showNotification(message, type = 'info') {
        // Check if notifications component exists
        if (window.notifications && window.notifications.show) {
            window.notifications.show(message, type);
        } else {
            // Fallback to console or simple alert
            console.log(`[${type.toUpperCase()}] ${message}`);
            
            // Could also show a simple toast or use browser notification
            if (type === 'error') {
                alert(message);
            }
        }
    }
    
    /**
     * Get CSRF token for requests
     * @returns {string}
     */
    getCsrfToken() {
        // Try HTMXManager first
        if (window.htmxManager && window.htmxManager.getCsrfToken) {
            return window.htmxManager.getCsrfToken();
        }
        
        // Fallback to DOM lookup
        const token = document.querySelector('[name=csrfmiddlewaretoken]');
        return token ? token.value : '';
    }
    
    /**
     * Extract product ID from element ID like "cart-qty-123"
     * @param {string} elementId 
     * @returns {string}
     */
    extractProductId(elementId) {
        return elementId.replace(/^cart-qty-/, '');
    }
    
    /**
     * Public API for template usage
     */
    
    // Legacy compatibility - these can be called from templates
    updateCartQuantity(productId, change, maxStock, newValue = null) {
        let quantity;
        if (newValue !== null) {
            quantity = parseInt(newValue) || 0;
        } else {
            const input = document.getElementById(`cart-qty-${productId}`);
            const currentValue = parseInt(input.value) || 1;
            quantity = Math.max(0, Math.min(maxStock, currentValue + change));
        }
        
        this.updateQuantity(productId, quantity);
    }
    
    removeFromCart(productId) {
        this.removeItem(productId);
    }
}

// Export for module usage
export default CartManager;

// Also create global instance for template usage
if (typeof window !== 'undefined') {
    window.cartManager = new CartManager();
    
    // Expose legacy functions for existing templates
    window.updateCartQuantity = (productId, change, maxStock, newValue = null) => {
        window.cartManager.updateCartQuantity(productId, change, maxStock, newValue);
    };
    
    window.removeFromCart = (productId) => {
        window.cartManager.removeFromCart(productId);
    };
}
