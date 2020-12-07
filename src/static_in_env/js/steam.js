function steam()
{
    const xhr = new XMLHttpRequest();
       const url = `https://cors-request-api-server.herokuapp.com/http://api.steampowered.com/IPlayerService/GetOwnedGames/v0001/?key=8308B03AE448D8C8081DDA432A5EBA91&steamid=76561198348203062&format=json`;
       xhr.open('GET', url, true);
       xhr.onload = function()
       {
           const data = JSON.parse(this.response);
           const response = data["response"]
           const gamecount =  response["game_count"]
           const arrayobject =  response["games"]

           let root = document.getElementById('steamCarousel');
           while (root.firstChild) {
               root.removeChild(root.firstChild);
           }
           let divid = document.getElementById('steamCarousel');
           divid.classList.add('testi_inner')

           let home_section_title = document.createElement('div');
           home_section_title.classList.add('home_section_title')
           let h1 = document.createElement('h1');
           h1.innerHTML = (`Number of Games: ${gamecount}`)
           home_section_title.appendChild(h1);
           divid.appendChild(home_section_title);

           let divcar = document.createElement('div');
           divcar.classList.add('carousel_container')
           divcar.classList.add('owl-carousel')

           for (let i in arrayobject)
           {
                let div = document.createElement('div');
                div.classList.add('carousel_items')

                var gamefinal = null;
                const xhr2 = new XMLHttpRequest();
                const appid = arrayobject[i].appid
                const gameurl = `https://cors-request-api-server.herokuapp.com/http://store.steampowered.com/api/appdetails?appids=${appid}`;
                xhr2.open('GET', gameurl, true);
                xhr2.onload = function()
                {
                    const indgamedata = JSON.parse(this.response);
                    const gamedata =  indgamedata[appid]
                    if(gamedata.hasOwnProperty('data'))
                    {
                       gamefinal =  gamedata["data"]
                       console.log(gamefinal)
                       div.innerHTML = (`
                         <div class="hero_capsule">
                           <a href="https://store.steampowered.com/app/1174180/Red_Dead_Redemption_2/?snr=1_4_660__651" class="hero_click_overlay"></a>
                                    <img class="hero_capsule_img" src="${gamefinal.header_image}" data-src="${gamefinal.header_image}">
                                    <div class="hover_screenshots">
                                       <div  data-background="url( https://steamcdn-a.akamaihd.net/steam/apps/1174180/ss_66b553f4c209476d3e4ce25fa4714002cc914c4f.600x338.jpg?t=1597419522  )" style="background-image: url(&quot;https://steamcdn-a.akamaihd.net/steam/apps/1174180/ss_66b553f4c209476d3e4ce25fa4714002cc914c4f.600x338.jpg?t=1597419522&quot;);">
                                          <video class="hero_video" onmouseover="this.play()" onmouseout="this.pause();this.currentTime=0;" loop autoplay preload="none" muted="muted">
                                             <source src="https://steamcdn-a.akamaihd.net/steam/apps/256768371/microtrailer.webm?t=1574881352?v=3" type="video/webm">
                                          </video>
                                       </div>
                                    </div>
                                    <div class="hero_data">
                                       <div class="hero_data_content">
                                          <div class="hero_name">Red Dead Redemption 2</div>
                                          <div class="hero_stat">
                                             <span class="label">Developer:</span>
                                             <span class="data">
                                                <a href="https://store.steampowered.com/developer/rockstargames?snr=1_4_660__629">Rockstar Games</a>
                                             </span>
                                          </div>
                                          <div class="hero_stat">
                                             <span class="label">Publisher:</span>
                                             <span class="data">
                                             <a href="https://store.steampowered.com/publisher/rockstargames?snr=1_4_660__629">Rockstar Games</a> </span>
                                          </div>
                                          <div class="hero_stat" data-tooltip-html="81% of the 121,621 user reviews for this game are positive.">
                                             <span class="label">All Reviews:</span>
                                             <span class="data">
                                                <span class="game_review_summary positive">
                                                   Very Positive </span>
                                                <span style="color: #AEAEAE; ">(121,621)</span>
                                             </span>
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
            lazyLoad:true,
            dots: false,
            autoplay: false,
            dots: true,
            autoplayTimeout: 2500,
            smartSpeed: 750,
            autoHeight:true,
            responsive: {
                0: {
                    items: 1
                },
                480: {
                    items: 2
                },
                768: {
                    items: 3
                },
                992: {
                    items: 4
                },
                1200: {
                    items: 5
                }
            }
        });
       }
       xhr.send();
}
