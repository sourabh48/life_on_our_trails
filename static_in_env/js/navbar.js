document.addEventListener("scroll", () => {
    const header = document.querySelector(".header_area");
    if (window.scrollY > 50) header.classList.add("scrolled");
    else header.classList.remove("scrolled");
});