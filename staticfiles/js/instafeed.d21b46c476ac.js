var feed = new Instafeed({

    accessToken: 'IGQVJYVi1wTndObGNqaGJmaWp1UlptOHVCcGszUHBlRmMwWVhXSFA5MG11MG5sRjV1emNTd1ZAyaGFzczFzR25JUDlQOTFzV01XQklPS0xfZA0t4QVI3MGJZAelc2UTZAIYnA2bHNMSVRrYzZALZAktnNVdmYwZDZD',
    template: '<div class="single-instaalbum"><a href="{{link}}"><img src="{{image}}" alt=""/><div class="instaalbum-info"><p>{{caption}}</p></div></a></div>',
    target: 'instafeed',
    resolution: 'standard_resolution',
    after: function () {
        $('.instafeed').slick({
            dots: false,
            infinite: true,
            speed: 300,
            slidesToShow: 6,
            slidesToScroll: 1,
            autoplay: true,
            autoplaySpeed: 2500,
            arrows: true,
            responsive: [
                {
                    breakpoint: 1024,
                    settings: {
                        slidesToShow: 5,
                        slidesToScroll: 5
                    }
                },
                {
                    breakpoint: 920,
                    settings: {
                        slidesToShow: 4,
                        slidesToScroll: 4
                    }
                },
                {
                    breakpoint: 720,
                    settings: {
                        slidesToShow: 3,
                        slidesToScroll: 3
                    }
                },
                {
                    breakpoint: 600,
                    settings: {
                        arrows: false,
                        slidesToShow: 2,
                        slidesToScroll: 2,
                        dots: true
                    }
                },
                {
                    breakpoint: 480,
                    settings: {
                        arrows: false,
                        slidesToShow: 1,
                        slidesToScroll: 1,
                        dots: true
                    }
                }
                // You can unslick at a given breakpoint now by adding:
                // settings: "unslick"
                // instead of a settings object
            ]
        });

    }
});

feed.run();
