function setupPaginationJump() {
  // Function to setup a single pagination input
  function setupSingleInput(inputId, position) {
    const input = document.getElementById(inputId);
    if (!input) return;
    
    // Remove any existing event listeners by cloning
    const newInput = input.cloneNode(true);
    input.parentNode.replaceChild(newInput, input);
    
    // Create the event handler on the fresh element
    newInput.addEventListener("keypress", function(e) {
      if (e.key === "Enter") {
        e.preventDefault();
        
        // Prevent multiple simultaneous pagination requests
        if (isPaginationJumping) {
          return;
        }
        
        const page = parseInt(this.value);
        const maxPages = parseInt(this.getAttribute("max"));
        
        // Validate page number
        if (isNaN(page) || page < 1 || page > maxPages) {
          this.value = ""; // Clear invalid input
          return;
        }
        
        isPaginationJumping = true;
        
        // Sync the value to the other pagination input
        const otherInputId = position === 'top' ? 'pagination-jump-input-bottom' : 'pagination-jump-input-top';
        const otherInput = document.getElementById(otherInputId);
        if (otherInput) {
          otherInput.value = page;
        }
        
        // Build URL for HTMX request
        const url = new URL(window.location);
        url.searchParams.set("page", page);
        
        // Use HTMX for pagination jump to maintain consistency
        htmx.ajax("GET", url.toString(), {
          target: "#product-list-container",
          swap: "outerHTML",
          headers: {
            "X-View-Preference": getViewPreference()
          }
        }).then(() => {
          isPaginationJumping = false;
          // Update URL in browser
          window.history.pushState({}, "", url.toString());
        }).catch((error) => {
          console.error("Pagination jump failed:", error);
          isPaginationJumping = false;
        });
      }
    });
  }
  
  // Setup both inputs using their IDs directly
  setupSingleInput('pagination-jump-input-top', 'top');
  setupSingleInput('pagination-jump-input-bottom', 'bottom');
}
