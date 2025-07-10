// Enhanced MPTT Tree Admin with Individual Node Manipulation
document.addEventListener('DOMContentLoaded', function() {
    console.log('Enhanced Tree Admin loading...');
    
    // Only run on category admin pages
    if (!document.querySelector('.djmptt-tree') && !document.querySelector('#changelist')) {
        return;
    }
    
    function refreshPage() {
        const indicator = document.createElement('div');
        indicator.style.cssText = `
            position: fixed; top: 50%; left: 50%; transform: translate(-50%, -50%);
            background: rgba(0,0,0,0.9); color: white; padding: 1rem 2rem;
            border-radius: 8px; z-index: 10000; font-weight: bold;
            box-shadow: 0 4px 20px rgba(0,0,0,0.3);
        `;
        indicator.textContent = 'Updating category tree...';
        document.body.appendChild(indicator);
        
        setTimeout(() => window.location.reload(), 1000);
    }
    
    // Wait for MPTT admin to load
    setTimeout(() => {
        enhanceTreeInterface();
    }, 500);
    
    function enhanceTreeInterface() {
        console.log('Enhancing tree interface...');
        
        // Override MPTT admin move function if available
        if (window.DjangoMpttAdmin && window.DjangoMpttAdmin.moveNode) {
            const originalMove = window.DjangoMpttAdmin.moveNode;
            
            window.DjangoMpttAdmin.moveNode = function(nodeId, targetId, position) {
                console.log('Enhanced move:', nodeId, '->', targetId, position);
                
                const result = originalMove.call(this, nodeId, targetId, position);
                
                // Auto-refresh after move
                if (result && result.then) {
                    result.then(() => {
                        console.log('Move successful, refreshing...');
                        refreshPage();
                    }).catch((error) => {
                        console.error('Move failed:', error);
                        refreshPage();
                    });
                } else {
                    setTimeout(refreshPage, 1500);
                }
                
                return result;
            };
            
            console.log('MPTT move function enhanced with auto-refresh');
        }
        
        // Enhance visual feedback for drag operations
        enhanceVisualFeedback();
        
        // Add keyboard shortcuts
        addKeyboardShortcuts();
    }
    
    function enhanceVisualFeedback() {
        const style = document.createElement('style');
        style.textContent = `
            /* Enhanced tree visual feedback */
            .djmptt-tree li:hover {
                background-color: #f8f9fa !important;
                border-radius: 4px !important;
                transition: all 0.2s ease !important;
            }
            
            .djmptt-tree .djmptt-dragging {
                opacity: 0.5 !important;
                transform: rotate(2deg) !important;
            }
            
            .djmptt-tree .djmptt-dragover {
                background-color: #e8f4fd !important;
                border: 2px dashed #007cba !important;
                border-radius: 4px !important;
            }
            
            .djmptt-tree .djmptt-drop-target {
                background-color: #d4edda !important;
                border: 2px solid #28a745 !important;
                border-radius: 4px !important;
            }
            
            /* Level-based color coding */
            .djmptt-tree .level-0 { border-left: 4px solid #6f42c1 !important; }
            .djmptt-tree .level-1 { border-left: 4px solid #007bff !important; }
            .djmptt-tree .level-2 { border-left: 4px solid #28a745 !important; }
            .djmptt-tree .level-3 { border-left: 4px solid #ffc107 !important; }
            .djmptt-tree .level-4 { border-left: 4px solid #fd7e14 !important; }
            
            /* Help text */
            .tree-help {
                background: #e7f3ff;
                border: 1px solid #b3d9ff;
                border-radius: 4px;
                padding: 10px;
                margin-bottom: 15px;
                font-size: 13px;
            }
            
            /* Success animation */
            .move-success {
                background-color: #d4edda !important;
                animation: fadeSuccess 3s ease-out !important;
            }
            
            @keyframes fadeSuccess {
                0% { background-color: #d4edda; }
                100% { background-color: transparent; }
            }
        `;
        document.head.appendChild(style);
        
        // Add helpful text at the top
        const helpDiv = document.createElement('div');
        helpDiv.className = 'tree-help';
        helpDiv.innerHTML = `
            <strong>🌳 Enhanced Tree Management:</strong> 
            Drag and drop any category to reorganize your tree structure. 
            Each node can be moved independently. Changes are saved automatically.
            <br><strong>Tip:</strong> Use Ctrl+R to manually refresh if needed.
        `;
        
        const contentMain = document.querySelector('#content-main');
        const results = document.querySelector('.results');
        if (contentMain && results) {
            contentMain.insertBefore(helpDiv, results);
        }
    }
    
    function addKeyboardShortcuts() {
        document.addEventListener('keydown', function(event) {
            // Ctrl+R or F5 - manual refresh
            if ((event.ctrlKey && event.key === 'r') || event.key === 'F5') {
                event.preventDefault();
                refreshPage();
            }
            
            // Ctrl+E - expand all nodes
            if (event.ctrlKey && event.key === 'e') {
                event.preventDefault();
                if (window.DjangoMpttAdmin && window.DjangoMpttAdmin.expandAll) {
                    window.DjangoMpttAdmin.expandAll();
                }
            }
            
            // Ctrl+C - collapse all nodes  
            if (event.ctrlKey && event.key === 'c') {
                event.preventDefault();
                if (window.DjangoMpttAdmin && window.DjangoMpttAdmin.collapseAll) {
                    window.DjangoMpttAdmin.collapseAll();
                }
            }
        });
        
        console.log('Keyboard shortcuts added: Ctrl+R (refresh), Ctrl+E (expand), Ctrl+C (collapse)');
    }
    
    // Monitor for successful moves and provide feedback
    const observer = new MutationObserver(function(mutations) {
        mutations.forEach(function(mutation) {
            if (mutation.type === 'childList') {
                // Tree structure changed, provide visual feedback
                const movedNodes = document.querySelectorAll('.djmptt-tree li[data-moved="true"]');
                movedNodes.forEach(node => {
                    node.classList.add('move-success');
                    node.removeAttribute('data-moved');
                    setTimeout(() => {
                        node.classList.remove('move-success');
                    }, 3000);
                });
            }
        });
    });
    
    const treeContainer = document.querySelector('.djmptt-tree');
    if (treeContainer) {
        observer.observe(treeContainer, { childList: true, subtree: true });
    }
    
    console.log('Enhanced Tree Admin loaded successfully! 🌳');
}); 