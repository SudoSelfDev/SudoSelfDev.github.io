document.addEventListener('DOMContentLoaded', () => {
    const themeToggle = document.getElementById('theme-toggle');
    const themeIcon = document.getElementById('theme-icon');
    
    // Check local storage for theme preference
    const savedTheme = localStorage.getItem('theme');
    if (savedTheme === 'light') {
        document.documentElement.classList.add('light-mode');
        themeIcon.textContent = 'dark_mode';
    }

    // Toggle theme
    themeToggle.addEventListener('click', () => {
        document.documentElement.classList.toggle('light-mode');
        
        if (document.documentElement.classList.contains('light-mode')) {
            themeIcon.textContent = 'dark_mode';
            localStorage.setItem('theme', 'light');
        } else {
            themeIcon.textContent = 'light_mode';
            localStorage.setItem('theme', 'dark');
        }
    });

    // Animate the circuit lines subtly
    const lines = document.querySelectorAll('.circuit-line-h, .circuit-line-v');
    lines.forEach(line => {
        // Random opacity pulse
        setInterval(() => {
            if (Math.random() > 0.7) {
                line.style.opacity = Math.random() * 0.5 + 0.1;
            }
        }, Math.random() * 2000 + 1000);
    });
});
