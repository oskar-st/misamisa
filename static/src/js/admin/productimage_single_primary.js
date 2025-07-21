// This script ensures only one 'is_primary' checkbox can be selected at a time in the ProductImage inline admin
(function() {
    function enforceSinglePrimary() {
        // Find all is_primary checkboxes in the inline
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
    // Run on DOMContentLoaded and after Django adds new inlines
    document.addEventListener('DOMContentLoaded', enforceSinglePrimary);
    // For dynamically added inlines (Django >=3.1+)
    document.body.addEventListener('formset:added', enforceSinglePrimary);
})(); 