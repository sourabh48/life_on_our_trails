function steam() {
    const xhr = new XMLHttpRequest();
    const url = `https://cors-request-api-server.herokuapp.com/http://api.steampowered.com/IPlayerService/GetOwnedGames/v0001/?key=8308B03AE448D8C8081DDA432A5EBA91&steamid=76561198348203062&format=json`;
    xhr.open('GET', url, true);
    xhr.onload = function () {
        const data = JSON.parse(this.response);
        const response = data["response"]
        const gamecount = response["game_count"]
        const arrayobject = response["games"]

        let root = document.getElementById('steamCarousel');
        while (root.firstChild) {
            root.removeChild(root.firstChild);
        }
        let divid = document.getElementById('steamCarousel');
        divid.classList.add('testi_inner')

        let home_section_title = document.createElement('div');
        home_section_title.classList.add('home_section_title')
        let h1 = document.createElement('h1');
        h1.innerHTML = (`Number of Games I Own: ${gamecount}`)
        home_section_title.appendChild(h1);
        divid.appendChild(home_section_title);

        let divcar = document.createElement('div');
        divcar.classList.add('carousel_container')
        divcar.classList.add('owl-carousel')

        for (let i in arrayobject) {
            let div = document.createElement('div');
            div.classList.add('carousel_items')

            var gamefinal = null;
            const xhr2 = new XMLHttpRequest();
            const appid = arrayobject[i].appid
            const gameurl = `https://cors-request-api-server.herokuapp.com/http://store.steampowered.com/api/appdetails?appids=${appid}`;
            xhr2.open('GET', gameurl, true);
            xhr.onerror = function () { // only triggers if the request couldn't be made at all
                console.log(`Network Error`);
            };
            xhr2.onload = function () {
                const indgamedata = JSON.parse(this.response);
                const gamedata = indgamedata[appid]
                if (gamedata["success"] == true) {
                    gamefinal = gamedata["data"]
                    // console.log(gamefinal)

                    var description = "";
                    for (i in gamefinal.genres) {
                        description += gamefinal.genres[i].description + ',  ';
                    }

                    div.innerHTML = (`
                         <div class="hero_capsule">
                            <div class="gamecontainer">
                                   <div class="game">
                                        <div class="hero_capsule_img">
                                              <img class="game-img" src="${gamefinal.header_image}" data-src="${gamefinal.header_image}">
                                        </div>
                                        <div class="text-game-cont">
                                            <div class="mr-grid">
                                                <div class="col1">
                                                    <h1>${gamefinal.name}</h1>
                                                    <div class="game-gen">
                                                        ${description}
                                                    </div>
                                                </div>
                                            </div>
                                            <div class="mr-grid summary-row">
                                                <div class="col2">
                                                    <h5>SUMMARY</h5>
                                                </div>
                                            </div>
                                            <div class="mr-grid">
                                                <div class="col1">
                                                    <p class="game-description">${gamefinal.short_description}</p>
                                                </div>
                                            </div>
                                            <div class="mr-grid">
                                                <span>Developer:</span>
                                                <span class="data">${gamefinal.developers}</span>
                                            </div>

                                            <div class="mr-grid">
                                                <span>Publishers:</span>
                                                <span class="data">${gamefinal.publishers}</span>
                                            </div>

                                            <div class="mr-grid">
                                                <span>Release Date:</span>
                                                <span class="data">${gamefinal.release_date.date}</span>
                                            </div>
                                        </div>
                                    </div>
                            </div>

                        `);
                }
            }
            xhr2.send();
            divcar.appendChild(div);
        }
        divid.appendChild(divcar);
        $('.owl-carousel').owlCarousel({
            loop: true,
            lazyLoad: true,
            dots: false,
            autoplay: true,
            dots: false,
            margin: 5,
            autoplayTimeout: 2500,
            smartSpeed: 750,
            responsive: {
                0: {
                    items: 1
                },
                620: {
                    items: 2
                },
                900: {
                    items: 3
                },
                1300: {
                    items: 4
                },
                1600: {
                    items: 5
                }
            }
        });
    }
    xhr.send();
}
