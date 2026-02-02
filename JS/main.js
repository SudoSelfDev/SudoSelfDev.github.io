const toggleLink = document.getElementById("darkToggle");

toggleLink.addEventListener("click", function (event) {
  event.preventDefault();

  // 1. Toggle the class on the body
  document.body.classList.toggle("dark-mode");

  // 2. Check if dark-mode is now active
  if (document.body.classList.contains("dark-mode")) {
    // If it is dark, change link text to "Light Mode"
    toggleLink.textContent = "☀️";
  } else {
    // If it's not dark, change link text back to "Dark Mode"
    toggleLink.textContent = "🌙";
  }
});
