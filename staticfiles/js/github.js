function my_cool_js_function(username) {
    const xhr = new XMLHttpRequest();
    const url = `https://api.github.com/users/${username}/repos`;
    xhr.open('GET', url, true);
    xhr.onload = function () {
        const data = JSON.parse(this.response);
        let root = document.getElementById('userRepos');
        while (root.firstChild) {
            root.removeChild(root.firstChild);
        }
        let divid = document.getElementById('userRepos');
        divid.classList.add('testi_inner')
        let p = document.createElement('p');
        p.innerHTML = (`
            <p><strong>Number of Public Repos:${data.length}</p>`)
        divid.appendChild(p);

        let divcar = document.createElement('div');
        divcar.classList.add('testi_slider')
        divcar.classList.add('owl-carousel')

        for (let i in data) {
            // Create variable that will create li's to be added to ul
            let div = document.createElement('div');
            // Add Bootstrap list item class to each li
            div.classList.add('item')

            if (data[i].description != null) {
                if (data[i].description.length > 90) {
                    // Create the html markup for each li
                    div.innerHTML = (`
                    <div class="testi_item card">
                        <h3>${data[i].name}</h4>
                        <p>${data[i].description.substring(0, 90)}...</p>
                        <a href="${data[i].html_url}"><i class="fa fa-github fa-3x"></i></a>
                    </div>
                `);
                } else {
                    // Create the html markup for each li
                    div.innerHTML = (`
                    <div class="testi_item card">
                        <h3>${data[i].name}</h4>
                        <p>${data[i].description.substring(0, 90)}</p>
                        <a href="${data[i].html_url}"><i class="fa fa-github fa-3x"></i></a>
                    </div>
                `);
                }
            } else {
                // Create the html markup for each li
                div.innerHTML = (`
                <div class="testi_item card">
                    <h3>${data[i].name}</h4>
                    <p>${data[i].description}</p>
                    <a href="${data[i].html_url}"><i class="fa fa-github fa-3x"></i></a>
                </div>
            `);
            }
            // Append each li to the ul
            divcar.appendChild(div);
        }
        divid.appendChild(divcar);
        $('.owl-carousel').owlCarousel({
            items: 4,
            margin: 4,
            loop: true,
            dots: false,
            autoplay: true,
            dots: true,
            autoplayTimeout: 2500,
            smartSpeed: 750,
            margin: 10,
            autoHeight: true,
            responsive: {
                380: {
                    items: 1
                },
                580: {
                    items: 1
                },
                668: {
                    items: 2
                },
                1092: {
                    items: 3
                }
            }
        });
    }


    // Send the request to the server
    xhr.send();
}