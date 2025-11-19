(function ($) {
    "use strict";

    var lastScroll = 0;
    var nav_offset_top = $('header').height() + 50;

    function navbarFixed() {
        if ($('.header_area').length) {
            $(window).on('scroll', function () {

                let scroll = $(this).scrollTop();
                let header = $(".header_area");

                /* ============================
                   1. Your original fixed navbar
                   ============================ */
                if (scroll >= nav_offset_top) {
                    header.addClass("navbar_fixed");
                } else {
                    header.removeClass("navbar_fixed");
                }

                /* ============================
                   2. Transparent when at top
                   ============================ */
                if (scroll <= 5) {
                    header.removeClass("nav-visible nav-hidden");
                    header.addClass("at-top");
                    lastScroll = scroll;
                    return;
                } else {
                    header.removeClass("at-top");
                }

                /* ============================
                   3. Hide on scroll down
                   ============================ */
                if (scroll > lastScroll) {
                    header.removeClass("nav-visible").addClass("nav-hidden");
                }

                /* ============================
                   4. Show on scroll up
                   ============================ */
                else {
                    header.removeClass("nav-hidden").addClass("nav-visible");
                }

                lastScroll = scroll;
            });
        }
    }

    navbarFixed();


    document.addEventListener("DOMContentLoaded", () => {
        const revealElements = document.querySelectorAll(".reveal, .reveal-stagger");

        const observer = new IntersectionObserver((entries) => {
            entries.forEach((entry, index) => {
                if (entry.isIntersecting) {
                    if (entry.target.classList.contains("reveal-stagger")) {
                        entry.target.style.transitionDelay = `${index * 120}ms`;
                    }
                    entry.target.classList.add("visible");
                }
            });
        }, {threshold: 0.2});

        revealElements.forEach((el) => observer.observe(el));
    });

    // ============================================================
// 1) SCROLL-REVEAL STAGGER ANIMATION
// ============================================================
    document.addEventListener("DOMContentLoaded", function () {
        const revealItems = document.querySelectorAll(".reveal-stagger");

        function revealOnScroll() {
            const trigger = window.innerHeight * 0.88;

            revealItems.forEach((el, i) => {
                const top = el.getBoundingClientRect().top;

                if (top < trigger && !el.classList.contains("visible")) {
                    setTimeout(() => {
                        el.classList.add("visible");
                    }, i * 120); // stagger per item
                }
            });
        }

        window.addEventListener("scroll", revealOnScroll);
        revealOnScroll();
    });

// ============================================================
// 2) CATEGORY FILTER CHIPS
// ============================================================
    document.addEventListener("DOMContentLoaded", function () {

        const chips = document.querySelectorAll(".chip");
        const cards = document.querySelectorAll(".allblogs-card");

        chips.forEach(chip => {
            chip.addEventListener("click", () => {

                // Switch active chip
                chips.forEach(c => c.classList.remove("active"));
                chip.classList.add("active");

                const filter = chip.dataset.filter;

                cards.forEach(card => {
                    const cat = card.dataset.category;

                    if (filter === "all" || filter === cat) {
                        card.style.display = "block";
                        setTimeout(() => card.classList.add("visible"), 50);
                    } else {
                        card.classList.remove("visible");
                        setTimeout(() => card.style.display = "none", 250);
                    }
                });
        });
    });

    });

    let infiniteScrollLoading = false;

    function loadMorePosts() {

        if (infiniteScrollLoading) return;

        const current = document.querySelector(".allblogs-pagination .active");
        const nextPageLink = current?.nextElementSibling?.querySelector("a");

        if (!nextPageLink) return;

        infiniteScrollLoading = true;

        fetch(nextPageLink.href, {headers: {"HX-Request": "true"}})
            .then(res => res.text())
            .then(html => {
                document
                    .querySelector(".allblogs-list")
                    .insertAdjacentHTML("beforeend", html);

                infiniteScrollLoading = false;
        });
    }

    window.addEventListener("scroll", function () {
        const bottomOffset = 300;
        const scrolled = window.innerHeight + window.scrollY;
        const documentHeight = document.body.offsetHeight;

        if (scrolled >= documentHeight - bottomOffset) {
            loadMorePosts();
        }
    });
    document.addEventListener("scroll", function () {
        document.querySelectorAll(".reveal").forEach(el => {
            let rect = el.getBoundingClientRect();
            if (rect.top < window.innerHeight - 80) {
                el.classList.add("active");
            }
        });
    });

// postimage limitter
    document.addEventListener("DOMContentLoaded", function () {
        document.querySelectorAll(".post-body img").forEach(img => {
            img.onload = function () {
                const ratio = img.naturalWidth / img.naturalHeight;

                if (ratio > 1.3) {
                    img.classList.add("landscape");      // WIDE
                } else if (ratio < 0.8) {
                    img.classList.add("portrait");       // TALL
                } else {
                    img.classList.add("square");         // SQUARE-LIKE
                }

                if (img.naturalHeight > img.naturalWidth * 2) {
                    img.classList.add("tall");           // EXTREME PORTRAIT
                }
            };
        });
    });

// code display
    document.addEventListener("DOMContentLoaded", async () => {

        const highlighter = await shiki.getHighlighter({
            theme: "github-dark",   // You can switch to: "nord", "dracula", "material-theme-darker"
        });

        document.querySelectorAll("pre code").forEach((block) => {

            const lang = block.className || "text";
            const code = block.innerText;

            // Highlight using Shiki
            const html = highlighter.codeToHtml(code, {lang});

            // Replace content
            const wrapper = document.createElement("div");
            wrapper.className = "code-wrapper";
            wrapper.innerHTML = html;

            // Add copy button
            const copyBtn = document.createElement("button");
            copyBtn.className = "code-copy-btn";
            copyBtn.innerHTML = `<i class="lnr lnr-copy"></i>`;
            copyBtn.addEventListener("click", () => {
                navigator.clipboard.writeText(code);
                copyBtn.classList.add("copied");
                copyBtn.innerHTML = "✓ Copied";
                setTimeout(() => {
                    copyBtn.classList.remove("copied");
                    copyBtn.innerHTML = `<i class="lnr lnr-copy"></i>`;
                }, 1500);
            });

            wrapper.appendChild(copyBtn);

            block.parentElement.replaceWith(wrapper);
        });
    });
})(jQuery)