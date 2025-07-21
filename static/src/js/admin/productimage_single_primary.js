// This script ensures only one 'is_primary' checkbox can be selected at a time in the ProductImage inline admin
(function() {
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
    document.addEventListener('DOMContentLoaded', enforceSinglePrimary);
    document.body.addEventListener('formset:added', enforceSinglePrimary); // For dynamically added inlines
})(); 