// Admin functionality for ProductImage inline admin
function enforceSinglePrimary() {
    const checkboxes = document.querySelectorAll('input[type="checkbox"][name$="-is_primary"]');
    checkboxes.forEach(function(checkbox) {
        checkbox.addEventListener('change', function() {
            if (this.checked) {
                checkboxes.forEach(function(other) {
                    if (other !== checkbox) {
                        other.checked = false;
                    }
                });
            }
        });
    });
}

// Initialize admin functionality
function initializeAdmin() {
    enforceSinglePrimary();
    
    // For dynamically added inlines
    document.body.addEventListener('formset:added', enforceSinglePrimary);
}

// Export for use in main.js
export { initializeAdmin }; 