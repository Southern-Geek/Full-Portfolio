        // Get references to elements
        const body = document.body;
        const toggleButton = document.getElementById('themeToggle');
        const toggleIcon = document.getElementById('toggleIcon');
        const toggleText = document.getElementById('toggleText');
        const status = document.getElementById('status');

        // Track current theme
        let isDark = false;

        // Function to update theme
        function updateTheme() {
            if (isDark) {
                body.className = 'dark';
                toggleIcon.textContent = '☀️';
                toggleText.textContent = 'Switch to Light Mode';
                status.innerHTML = '☾ Dark Mode';
            } else {
                body.className = 'light';
                toggleIcon.textContent = '☾';
                toggleText.textContent = 'Switch to Dark Mode';
                status.innerHTML = '☀️ Light Mode';
            }
        }

        // Add click event listener to toggle button
        toggleButton.addEventListener('click', function() {
            isDark = !isDark;
            updateTheme();
            
            // Add a little animation feedback
            toggleButton.style.transform = 'scale(0.95)';
            setTimeout(() => {
                toggleButton.style.transform = '';
            }, 150);
        });

        // Initialize theme
        updateTheme();

        // Optional: Add keyboard support
        toggleButton.addEventListener('keydown', function(e) {
            if (e.key === 'Enter' || e.key === ' ') {
                e.preventDefault();
                toggleButton.click();
            }
        });
