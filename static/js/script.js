
// Auto-hide flash messages after 5 seconds
document.addEventListener('DOMContentLoaded', function() {
    // Auto hide after 5 seconds
    setTimeout(function() {
        document.querySelectorAll('.flash-message').forEach(function(message) {
            message.remove();
        });
    }, 5000);

    // Manual close functionality
    document.querySelectorAll('.flash-close').forEach(function(button) {
        button.addEventListener('click', function() {
            this.closest('.flash-message').remove();
        });
    });
});



// Context menu on user icon 
document.addEventListener('DOMContentLoaded', function() {
    const userMenuButton = document.getElementById('userMenuButton');
    const userMenu = document.getElementById('userMenu');
    
    // Toggle menu on button click
    userMenuButton.addEventListener('click', function(e) {
        e.stopPropagation();
        userMenu.classList.toggle('hidden');
    });
    
    // Close menu when clicking outside
    document.addEventListener('click', function() {
        userMenu.classList.add('hidden');
    });
});
