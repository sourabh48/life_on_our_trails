document.addEventListener("DOMContentLoaded", function () {
    const items = document.querySelectorAll(".fade-section");

    const observer = new IntersectionObserver(
        entries => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add("visible");
                    observer.unobserve(entry.target);  // animate once
                }
            });
        },
        {
            threshold: 0.2, // triggers when 20% is visible
        }
    );

    items.forEach(item => observer.observe(item));
});
