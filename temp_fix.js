    // Handle sidebar category navigation - ONLY preserve view for shop pages
    if (triggerElement && 
        triggerElement.closest('.sidebar-categories') && 
        this.isViewSwitchablePage()) {
      // DISABLED: Don't manipulate sidebar URLs, let them work naturally
      console.log('Sidebar navigation detected but URL manipulation disabled');
    }
