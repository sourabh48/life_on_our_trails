var youtube_global_options = {};


(function ($) {


    var secondsToTime = function (duration) {
            if (null == duration || duration == "" || duration == "undefined")
                return "?";

            var minutes = Math.floor(duration / 60);
            //alert(minutes);

            var seconds = duration % 60;

            if (seconds < 10)
                seconds = "0" + seconds;

            var time = minutes + ":" + seconds;
            return time;
            //alert()

        },

        convertDuration = function (videoDuration) {
            var duration, returnDuration;
            videoDuration = videoDuration.replace('PT', '').replace('S', '').replace('M', ':').replace('H', ':');


            var videoDurationSplit = videoDuration.split(':');
            returnDuration = videoDurationSplit[0];
            for (var i = 1; i < videoDurationSplit.length; i++) {
                duration = videoDurationSplit[i];
                ////console.log('duration-'+duration);
                if (duration == "") {
                    returnDuration += ":00";
                } else {
                    duration = parseInt(duration, 10);
                    ////console.log('duration else -'+duration)
                    if (duration < 10) {
                        returnDuration += ":0" + duration;
                    } else {
                        returnDuration += ":" + duration;
                    }
                }
            }
            if (videoDurationSplit.length == 1) {
                returnDuration = "0:" + returnDuration;
            }
            return returnDuration;

        },


        getDateDiff = function (timestamp) {
            if (null == timestamp || timestamp == "" || timestamp == "undefined")
                return "?";
            //alert(timestamp);
            var splitDate = ((timestamp.toString().split('T'))[0]).split('-');
            var d1 = new Date();

            var d1Y = d1.getFullYear();
            var d2Y = parseInt(splitDate[0], 10);
            var d1M = d1.getMonth();
            var d2M = parseInt(splitDate[1], 10);

            var diffInMonths = (d1M + 12 * d1Y) - (d2M + 12 * d2Y);
            if (diffInMonths <= 1)
                return "1 month ";
            else if (diffInMonths < 12)
                return diffInMonths + " months ";

            var diffInYears = Math.floor(diffInMonths / 12);

            if (diffInYears <= 1)
                return "1 year";
            else if (diffInYears < 12)
                return diffInYears + " years";

        },

        getReadableNumber = function (number) {
            if (null == number || number == "" || number == "undefined")
                return "?";

            number = number.toString();
            var readableNumber = '';
            var count = 0;
            for (var k = number.length; k >= 0; k--) {
                readableNumber += number.charAt(k);
                if (count == 3 && k > 0) {
                    count = 1;
                    readableNumber += ',';
                } else {
                    count++;
                }
            }
            return readableNumber.split("").reverse().join("");
        },


        loadYoutube = function () {

            youtubeWidgetWidth = $('#youtube').width();

            $('#youtube').append('<div id="youtube-header"><div id="youtube-stat-holder"></div></div>');

            //$('#youtube').append('<div id="youtube-tabs"></div>');

            $('#youtube').append('<div id="youtube-tabs"><!--<span id="featured_" class="youtube-tab">Featured</span>--><span id="uploads_" class="youtube-tab">Latest Videos</span><!--<span id="playlists_" class="youtube-tab">Playlists</span></div>-->');


            $('#youtube').append('<div id="youtube-encloser"><iframe id="youtube-video" width="' + (youtubeWidgetWidth - 2) + '" height="' + (youtubeWidgetWidth / youtube_global_options.youtubeVideoAspectRatio) + '" src="" frameborder="0" allowfullscreen></iframe><div id="youtube-video-list-div"></div><div id="youtube-load-more-div">SEE MORE VIDEOS</div></div>');

            $('#youtube-video').hide();

            $('#youtube').append('<div id="youtube-lightbox"><div style="width:100%; position:absolute; top:20%;"><iframe id="youtube-video-lightbox" width="640" height="360" src="" frameborder="0" allowfullscreen></iframe></div></div>');

            $('#youtube-lightbox').hide();
        },

        //get channel Id if channel URL is of the form ....../user/Adele
        getChannelId = function (apiUrl) {
            //console.log('inside getChannelId');
            //console.log('apiUrl-'+apiUrl);
            //showLoader();

            $.ajax({
                url: apiUrl,
                type: "GET",
                async: true,
                cache: true,
                dataType: 'jsonp',
                success: function (response) {
                    youtubeChannelId = response.items[0].id
                    getChannelDetails(youtubeChannelId);
                },
                error: function (html) {
                    alert(html);
                },
                beforeSend: setHeader
            });
        },


        getChannelDetails = function (channelId) {

            //var apiProfileURL = "http://gdata.youtube.com/feeds/api/users/"+youtubeUser+"?v=2&alt=json";
            var apiProfileURL = "https://www.googleapis.com/youtube/v3/channels?part=brandingSettings%2Csnippet%2Cstatistics%2CcontentDetails&id=" + channelId + "&key=" + youtube_global_options.apiKey;

            $.ajax({
                url: apiProfileURL,
                type: "GET",
                async: true,
                cache: true,
                dataType: 'jsonp',
                success: function (response) {
                    showInfo(response);
                },
                error: function (html) {
                    alert(html);
                },
                beforeSend: setHeader
            });

        },


        setHeader = function (xhr) {
            if (xhr && xhr.overrideMimeType) {
                xhr.overrideMimeType("application/j-son;charset=UTF-8");
            }
        },

        showLoader = function () {
            youtube_global_options.youtubeItemCount = 0;
            $('#youtube-video-list-div').empty();
            $('#youtube-video').hide();
            $('#youtube-video').attr('src', '');
            $('#youtube-video-list-div').append('<div style="text-align:center; height:200px; font:14px Calibri;"><br><br><br><br><br><br>Loading...</div>');
        },

        initFeaturedVideos = function () {
            youTubePlaylistURL = youtube_global_options.youTubePlaylistURL;
            console.log('inside init featured - ' + youTubePlaylistURL);
            if (null != youTubePlaylistURL && youTubePlaylistURL.indexOf("youtube.com/playlist?list=") != -1) {
                youtubeFeaturedPlaylistId = youTubePlaylistURL.substring(youTubePlaylistURL.indexOf("?list=") + 6);
                youtube_global_options.youtubeFeaturedPlaylistId = youtubeFeaturedPlaylistId;
            }
        },


        showInfo = function (response) {
            console.log('showInfo');
            console.log(response);

            var channelData = response.items[0];
            var channelId = channelData.id;
            var channelName = channelData.snippet.title;
            var channelPic = channelData.snippet.thumbnails.default.url;
            var channelSubscribers = channelData.statistics.subscriberCount;
            var channelViews = channelData.statistics.viewCount;
            var channelDesc = "";
            var channelUploadsPlaylistId = channelData.contentDetails.relatedPlaylists.uploads;


            $('#youtube-header').append('<img id="youtube-header-logo" src="' + channelPic + '"/>' + channelName);

            $('#youtube-header').append('&nbsp;&nbsp;&nbsp;&nbsp;<div class="youtube-subscribe"><div class="g-ytsubscribe" data-channelid="' + channelId + '" data-layout="default" data-count="default"></div></div>');

            //$('#youtube-stat-holder').append('<div class="youtube-stat">'+channelSubscribers+'<br/> subscribers </div><div class="youtube-stat">'+channelViews+'<br/>video views</div>');

            //$('#youtube-stat-holder').append('<div class="youtube-stat"><span class="youtube-stat-count">'+getReadableNumber(channelViews)+'</span><br/> video views </div><div class="youtube-stat"><span class="youtube-stat-count">'+getReadableNumber(channelSubscribers)+'</span><br/>subscribers</div>');

            //$('#youtube-channel-desc').append('About '+channelName+'<br/>'+channelDesc);

            renderSubscribeButton();

            $('#youtube-tabs').find('span[id^=uploads_]').attr('id', 'uploads_' + channelUploadsPlaylistId);

            youtubeDefaultTab = youtube_global_options.youtubeDefaultTab;

            if (typeof youtubeDefaultTab === 'undefined' || null == youtubeDefaultTab || youtubeDefaultTab == "" || youtubeDefaultTab == "undefined") {
                $("#youtube-tabs span[id^=featured_]").click();
            } else if (youtubeDefaultTab.toUpperCase() == 'UPLOADS' || youtubeDefaultTab.toUpperCase() == 'UPLOAD') {
                $("#youtube-tabs span[id^=uploads_]").click();
            } else if (youtubeDefaultTab.toUpperCase() == 'PLAYLISTS' || youtubeDefaultTab.toUpperCase() == 'PLAYLIST') {
                $("#youtube-tabs span[id^=playlists_]").click();
            } else if (youtubeDefaultTab.toUpperCase() == 'FEATURED' || youtubeDefaultTab.toUpperCase() == 'FEATURED') {
                $("#youtube-tabs span[id^=featured_]").click();
            }


        },

        renderSubscribeButton = function () {
            $.ajaxSetup({
                cache: true
            });

            $.getScript("https://apis.google.com/js/platform.js")
                .done(function (script, textStatus) {
                    //alert( textStatus );
                })
                .fail(function (jqxhr, settings, exception) {
                    //alert( "Triggered ajaxError handler." );
                });
        },


        showPlaylists = function (response, loadMoreFlag) {
            console.log(response);

            if (!loadMoreFlag) {
                $('#youtube-video-list-div').empty();
            }

            var nextPageToken = response.nextPageToken;
            var $youtubeLoadMoreDiv = $('#youtube-load-more-div');
            //console.log('nextPageToken-'+nextPageToken);

            if (null != nextPageToken && nextPageToken != "undefined" && nextPageToken != "") {
                $youtubeLoadMoreDiv.data('nextpagetoken', nextPageToken);
            } else {
                $youtubeLoadMoreDiv.data('nextpagetoken', '');
            }

            youtubeColumns = youtube_global_options.youtubeColumns;

            var playlistArray = response.items;
            var playlistIdArray = [];
            var zeroPlaylistCompensation = 0;
            for (var i = 0; i < playlistArray.length; i++) {
                playListId = playlistArray[i].id;
                playlistSize = playlistArray[i].contentDetails.itemCount;
                if (playlistSize <= 0) {
                    zeroPlaylistCompensation++;
                    continue;
                }
                playlistIdArray.push(playListId);
                playlistTitle = playlistArray[i].snippet.title;
                playlistUploaded = playlistArray[i].snippet.publishedAt;
                playlistThumbnail = playlistArray[i].snippet.thumbnails.medium.url;
                //playlistThumbnail = playlistThumbnail.replace("hqdefault","mqdefault");
                if ((i + youtube_global_options.youtubeItemCount - zeroPlaylistCompensation) % youtubeColumns != 0)
                    $('#youtube-video-list-div').append('<div class="youtube-video-tnail-box" style="width:' + ((100 / youtubeColumns) - 4) + '%;" id="' + playListId + '"><div class="youtube-video-tnail" style="filter: progid:DXImageTransform.Microsoft.AlphaImageLoader( src=\'' + playlistThumbnail + '\', sizingMethod=\'scale\'); background-image:url(\'' + playlistThumbnail + '\')"><div class="youtube-playlist-sidebar" id="youtube-playlist-sidebar-' + playListId + '"><span class="youtube-playlist-video-count"><b>' + playlistSize + '</b><br/>VIDEOS</span></div></div><span class="youtube-video-list-title">' + playlistTitle + '</span><br/><span class="youtube-video-list-views">' + getDateDiff(playlistUploaded) + ' ago</span></div>');
                else
                    $('#youtube-video-list-div').append('<div class="youtube-video-tnail-box" style="width:' + ((100 / youtubeColumns) - 4) + '%; clear:both;" id="' + playListId + '"><div class="youtube-video-tnail" style="filter: progid:DXImageTransform.Microsoft.AlphaImageLoader( src=\'' + playlistThumbnail + '\', sizingMethod=\'scale\'); background-image:url(\'' + playlistThumbnail + '\')"><div class="youtube-playlist-sidebar" id="youtube-playlist-sidebar-' + playListId + '"><span class="youtube-playlist-video-count"><b>' + playlistSize + '</b><br/>VIDEOS</span></div></div><span class="youtube-video-list-title">' + playlistTitle + '</span><br/><span class="youtube-video-list-views">' + getDateDiff(playlistUploaded) + ' ago</span></div>');

            }

            youtube_global_options.youtubeItemCount += playlistArray.length - zeroPlaylistCompensation;
            //console.log(playlistIdArray);

            $('.youtube-video-tnail-box').click(function () {
                //alert(this.id);
                showLoader();
                playlistTitle = $(this).find(".youtube-video-list-title").text();
                getUploads("play_" + this.id, playlistTitle);
                //getPlaylistVideos(this.id);
            });


            resetLoadMoreButton();

            //console.log(youtubeTnailWidth);
            //console.log(youtubeTnailHeight);

            //getTopVideosFromPlaylist(playlistIdArray,maxTopVideos);
        },

        showUploads = function (response, playlistTitle, loadMoreFlag) {
            console.log(response);

            if (!loadMoreFlag) {
                $('#youtube-video-list-div').empty();

                if (playlistTitle) {
                    $('.youtube-tab-hover').removeClass('youtube-tab-hover');
                    $('#youtube-video-list-div').append('<span class="youtube-showing-title youtube-tab-hover" id="uploads_' + response.items[0].snippet.playlistId + '" style="max-width:100%;"><span class="youtube-showing">&nbsp;&nbsp;Showing playlist: </span>' + playlistTitle + '</span><br/>');
                }
            }

            var nextPageToken = response.nextPageToken;
            var $youtubeLoadMoreDiv = $('#youtube-load-more-div');
            //console.log('nextPageToken-'+nextPageToken);

            youtubeColumns = youtube_global_options.youtubeColumns;

            if (null != nextPageToken && nextPageToken != "undefined" && nextPageToken != "") {
                $youtubeLoadMoreDiv.data('nextpagetoken', nextPageToken);
            } else {
                $youtubeLoadMoreDiv.data('nextpagetoken', '');
            }

            var uploadsArray = response.items;
            var videoIdArray = [];

            for (var i = 0; i < uploadsArray.length; i++) {
                videoId = uploadsArray[i].snippet.resourceId.videoId;
                videoTitle = uploadsArray[i].snippet.title;
                //videoViewCount = uploadsArray[i].snippet.viewCount;
                //videoDuration = uploadsArray[i].snippet.duration;
                videoUploaded = uploadsArray[i].snippet.publishedAt;
                videoThumbnail = uploadsArray[i].snippet.thumbnails.medium.url;
                //videoThumbnail = videoThumbnail.replace("hqdefault","mqdefault");

                videoIdArray.push(videoId);

                //$('#youtube-video-list-div').append('<div class="youtube-video-tnail-box" style="width:'+((100/youtubeColumns)-4)+'%;" id="'+videoId+'"><div class="youtube-video-tnail" style="filter: progid:DXImageTransform.Microsoft.AlphaImageLoader( src=\''+videoThumbnail+'\', sizingMethod=\'scale\'); background-image:url(\''+videoThumbnail+'\')"><div class="youtube-duration">'+secondsToTime(videoDuration)+'</div></div><span class="youtube-video-list-title">'+videoTitle+'</span><br/><span class="youtube-video-list-views">'+getReadableNumber(videoViewCount)+' views | '+getDateDiff(videoUploaded)+' ago</span></div>');


                if ((i + youtube_global_options.youtubeItemCount) % youtubeColumns != 0)
                    $('#youtube-video-list-div').append('<div class="youtube-video-tnail-box" style="width:' + ((100 / youtubeColumns) - 4) + '%;" id="' + videoId + '"><div class="youtube-video-tnail" style="filter: progid:DXImageTransform.Microsoft.AlphaImageLoader( src=\'' + videoThumbnail + '\', sizingMethod=\'scale\'); background-image:url(\'' + videoThumbnail + '\')"><div class="youtube-duration"></div></div><span class="youtube-video-list-title">' + videoTitle + '</span><br/><span class="youtube-video-list-views">' + getDateDiff(videoUploaded) + 'ago</span></div>');
                else
                    $('#youtube-video-list-div').append('<div class="youtube-video-tnail-box" style="width:' + ((100 / youtubeColumns) - 4) + '%; clear:both;" id="' + videoId + '"><div class="youtube-video-tnail" style="filter: progid:DXImageTransform.Microsoft.AlphaImageLoader( src=\'' + videoThumbnail + '\', sizingMethod=\'scale\'); background-image:url(\'' + videoThumbnail + '\')"><div class="youtube-duration"></div></div><span class="youtube-video-list-title">' + videoTitle + '</span><br/><span class="youtube-video-list-views">' + getDateDiff(videoUploaded) + ' ago</span></div>');

            }

            youtube_global_options.youtubeItemCount += uploadsArray.length;

            $('.youtube-video-tnail-box').click(function () {
                //alert(this.id);
                //alert(showVideoInLightbox);
                if (youtube_global_options.showVideoInLightbox) {
                    showVideoLightbox(this.id);
                } else {
                    $('#youtube-video').attr('src', 'http://www.youtube.com/embed/' + this.id);
                    $('#youtube-video').show();
                    $('html,body').animate({
                        scrollTop: $("#youtube-header").offset().top
                    }, 'slow');
                }
            });


            getVideoStats(videoIdArray);
            resetLoadMoreButton();

        },


        //get video stats using Youtube API
        getVideoStats = function (videoIdList) {

            apiVideoStatURL = "https://www.googleapis.com/youtube/v3/videos?part=statistics%2CcontentDetails&id=" + videoIdList + "&key=" + youtube_global_options.apiKey;
            $.ajax({
                url: apiVideoStatURL,
                type: "GET",
                async: true,
                cache: true,
                dataType: 'jsonp',
                success: function (response) {
                    displayVideoStats(response);
                },
                error: function (html) {
                    alert(html);
                },
                beforeSend: setHeader
            });
        },

        //display video statistics
        displayVideoStats = function (response) {
            //console.log(response);

            var videoArray = response.items;
            var $videoThumbnail;

            for (var i = 0; i < videoArray.length; i++) {
                videoId = videoArray[i].id;
                videoViewCount = videoArray[i].statistics.viewCount;
                videoViewCount = getReadableNumber(videoViewCount);
                videoDuration = videoArray[i].contentDetails.duration;
                //console.log('videoDuration-'+videoDuration);

                videoDuration = convertDuration(videoDuration);
                videoDefinition = videoArray[i].contentDetails.definition.toUpperCase();
                $videoThumbnail = $('#youtube-video-list-div #' + videoId);
                $videoThumbnail.find('.youtube-video-list-views').prepend(videoViewCount + ' views | ');
                $videoThumbnail.find('.youtube-duration').append(videoDuration);
                //$videoThumbnail.append('<div class="youtube-definition">'+videoDefinition+'</div>');

            }
        },


        getUploads = function (youtubeTabId, playlistTitle, nextPageToken) {
            //showLoader();
            //var apiUploadURL = "http://gdata.youtube.com/feeds/api/users/"+youtubeUser+"/uploads/?v=2&alt=jsonc&max-results=50";

            var pageTokenUrl = "";
            var loadMoreFlag = false;

            if (null != nextPageToken) {
                pageTokenUrl = "&pageToken=" + nextPageToken;
                loadMoreFlag = true;
            }

            var uploadsPlaylistId = youtubeTabId.substring(youtubeTabId.indexOf('_') + 1);
            var apiUploadURL = "https://www.googleapis.com/youtube/v3/playlistItems?part=snippet&playlistId=" + uploadsPlaylistId + "&maxResults=" + youtube_global_options.maxResults + pageTokenUrl + "&key=" + youtube_global_options.apiKey;

            console.log('apiUploadURL-' + apiUploadURL);

            $.ajax({
                url: apiUploadURL,
                type: "GET",
                async: true,
                cache: true,
                dataType: 'jsonp',
                success: function (response) {
                    showUploads(response, playlistTitle, loadMoreFlag);
                },
                error: function (html) {
                    alert(html);
                },
                beforeSend: setHeader
            });
        },


        getPlaylists = function (nextPageToken) {

            var pageTokenUrl = "";
            var loadMoreFlag = false;

            if (null != nextPageToken) {
                pageTokenUrl = "&pageToken=" + nextPageToken;
                loadMoreFlag = true;
            }

            var apiChannelPlaylistsURL = "https://www.googleapis.com/youtube/v3/playlists?part=contentDetails,snippet&channelId=" + youtubeChannelId + "&maxResults=" + youtube_global_options.maxResults + pageTokenUrl + "&key=" + youtube_global_options.apiKey;

            //var apiPlaylistURL = "https://gdata.youtube.com/feeds/api/users/"+youtubeUser+"/playlists?v=2&alt=jsonc&max-results=50";
            $.ajax({
                url: apiChannelPlaylistsURL,
                type: "GET",
                async: true,
                cache: true,
                dataType: 'jsonp',
                success: function (response) {
                    showPlaylists(response, loadMoreFlag);
                },
                error: function (html) {
                    alert(html);
                },
                beforeSend: setHeader
            });
        },

        showVideoLightbox = function (videoId) {
            $('#youtube-lightbox').show();
            $('#youtube-video-lightbox').attr('src', 'http://www.youtube.com/embed/' + videoId);

            $('#youtube-lightbox').click(function () {
                $('#youtube-video-lightbox').attr('src', '');
                $('#youtube-lightbox').hide();
            });
        },

        resetLoadMoreButton = function () {
            var $youtubeLoadMoreDiv = $('#youtube-load-more-div');
            $youtubeLoadMoreDiv.removeClass('youtube-load-more-div-click');
            $youtubeLoadMoreDiv.text('Load More Videos');
        },

        prepareYoutube = function () {
            $('#youtube').empty();


            loadYoutube();
            showLoader();

            $('.youtube-tab').click(function () {
                $('.youtube-tab-hover').removeClass('youtube-tab-hover');
                $(this).addClass('youtube-tab-hover');
                //$('.youtube-tab').css('color','#666');
                //$('.youtube-tab').css('background-color','rgb(230,230,230)');
                //$('.youtube-tab').css('text-shadow','0 1px 0 #fff');

                //$(this).css('color','#eee');
                //$(this).css('background-color','#999');
                //$(this).css('text-shadow','0 0');

                youtubeTabId = this.id;

                showLoader();

                if (youtubeTabId.indexOf("featured_") != -1) {
                    getUploads('featured_' + youtube_global_options.youtubeFeaturedPlaylistId, null, null);
                } else if (youtubeTabId.indexOf("uploads_") != -1) {
                    getUploads(youtubeTabId);
                } else if (youtubeTabId.indexOf("playlists_") != -1) {
                    getPlaylists();
                }
            });

            $('#youtube-load-more-div').click(function () {

                var $youtubeLoadMoreDiv = $('#youtube-load-more-div');
                $youtubeLoadMoreDiv.html('LOADING..');
                $youtubeLoadMoreDiv.addClass('youtube-load-more-div-click');

                var youtubeTabId = $('.youtube-tab-hover').attr('id');
                var nextPageToken = $youtubeLoadMoreDiv.data('nextpagetoken');
                console.log('load more clicked : nextPageToken-' + nextPageToken);

                if (null != nextPageToken && nextPageToken != "undefined" && nextPageToken != "") {
                    if (youtubeTabId.indexOf("featured_") != -1) {
                        getUploads('featured_' + youtube_global_options.youtubeFeaturedPlaylistId, null, nextPageToken);
                    } else if (youtubeTabId.indexOf("uploads_") != -1) {
                        getUploads(youtubeTabId, null, nextPageToken);
                    } else if (youtubeTabId == "playlists_") {
                        getPlaylists(nextPageToken);
                    }
                } else {
                    $youtubeLoadMoreDiv.html('ALL DONE');
                }

            });

            youTubeChannelURL = youtube_global_options.youTubeChannelURL;

            //Get Channel header and details
            if (youTubeChannelURL != null) {
                s = youTubeChannelURL.indexOf("/user/");
                ////console.log('s-'+s);
                if (s != -1) {
                    userId = youTubeChannelURL.substring(s + 6);
                    //console.log('userId-'+userId);
                    apiUrl = "https://www.googleapis.com/youtube/v3/channels?part=id&forUsername=" + userId + "&key=" + youtube_global_options.apiKey;
                    getChannelId(apiUrl);
                } else {
                    s = youTubeChannelURL.indexOf("/channel/");
                    if (s != -1) {
                        youtubeChannelId = youTubeChannelURL.substring(s + 9);
                        youtube_global_options.youtubeChannelId = youtubeChannelId;
                        getChannelDetails(youtubeChannelId);
                    } else {
                        alert("Could Not Find Channel..");
                    }
                }
            }

        }


    $.fn.youtube = function (options) {


        //set local options
        youtube_global_options.apiKey = options.apiKey;
        youtube_global_options.youTubeChannelURL = options.youTubeChannelURL || '';
        youtube_global_options.youTubePlaylistURL = options.youTubePlaylistURL || '';
        youtube_global_options.youtubeDefaultTab = options.youtubeDefaultTab || 'FEATURED';
        youtube_global_options.youtubeColumns = options.youtubeColumns || 3;
        youtube_global_options.showVideoInLightbox = options.showVideoInLightbox || false;
        youtube_global_options.youtubeChannelId = '';
        youtube_global_options.maxResults = options.maxResults || 15;
        youtube_global_options.youtubeItemCount = 0;
        youtube_global_options.youtubeVideoAspectRatio = 640 / 360;

        youtube_global_options.youtubeMqdefaultAspectRatio = 300 / 180;

        initFeaturedVideos();
        prepareYoutube();

    };


}(jQuery));
