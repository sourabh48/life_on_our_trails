var swiper = new Swiper(".blogSwiper", {
    loop: true,
    grabCursor: true,
    spaceBetween: 30,
    autoHeight: true,

    autoplay: {
        delay: 2500,
        disableOnInteraction: false,
    },

    pagination: {
        el: ".swiper-pagination",
        clickable: true,
    },

    navigation: {
        nextEl: ".swiper-button-next",
        prevEl: ".swiper-button-prev",
    },

    keyboard: {
        enabled: true,
        onlyInViewport: true,
    },

    mousewheel: {
        forceToAxis: true,
        sensitivity: 1.2,
    },

    breakpoints: {
        0: {slidesPerView: 1},
        576: {slidesPerView: 1},
        768: {slidesPerView: 2},
        1200: {slidesPerView: 3}
    }
});

/* ---------------------------------------------
   AUTOPLAY PAUSE ON HOVER
---------------------------------------------- */
const swiperEl = document.querySelector(".blogSwiper");

swiperEl.addEventListener("mouseenter", () => {
    swiper.autoplay.stop();
});

swiperEl.addEventListener("mouseleave", () => {
    swiper.autoplay.start();
});