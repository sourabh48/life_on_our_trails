document.addEventListener("DOMContentLoaded", () => {

    const animatedItems = document.querySelectorAll(".stagger");

    const observer = new IntersectionObserver(
        (entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {

                    // Begin animation
                    entry.target.style.animationPlayState = "running";

                    // Once animated, stop observing (prevents repeat)
                    observer.unobserve(entry.target);
                }
            });
        },
        {
            threshold: 0.2   // 20% visible triggers animation
        }
    );

    animatedItems.forEach(item => observer.observe(item));

});
