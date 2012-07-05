var AudioPlayer = Backbone.Model.extend({
    defaults: {
        audio: new Audio(),
        playlist: [],
        playlistPosition: 0,
        current: {},
        playing: false,
    },

    initialize: function() {
        this.on('change:current', function() {
            var audio = this.get('audio');
            var position = this.get('playlistPosition');
            var track = this.get('playlist')[position];

            audio.src = '/song/' + track.id;
        }, this);

        jQuery.getJSON('/songs', _.bind(function(data) {
            this.set({
                current: data[0],
                playlist: data
            });
        }, this));
    },

    isPaused: function() {
        return !this.get('playing');
    },

    play: function() {
        this.get('audio').play();
        this.set({playing: true});
    },

    pause: function() {
        this.get('audio').pause();
        this.set({playing: false});
    }
});

var ApplicationView = Backbone.View.extend({
    el: 'body',

    initialize: function() {
        var audioplayer = new AudioPlayer();

        // Song changed
        audioplayer.on('change:current', function() {
            var current = this.get('current');

            $('h1').text(current.title);
            $('h2').text(current.artist);
            $('head title').text(current.artist + ' - ' + current.title);

        }, audioplayer);

        // Play/Pause
        audioplayer.on('change:playing', function() {
            var vinyl = $('.vinyl');

            if (this.get('playing')) {
                if (!vinyl.hasClass('visible')) {
                  vinyl.addClass('visible');
                }
            } else {
                vinyl.removeClass('visible');
            }
        }, audioplayer);

        // Animate the cover when fully loaded
        $('h1, h2').css({opacity: 0});
        $('.cover').load(function() {
            $('.album').css({
                opacity: 1,
                perspective: '604px',
                rotateY: '90deg',
            });

            setTimeout(function() {
                $('.album').transition({
                    rotateY: '0deg'
                }, 1000, 'ease');

                setTimeout(function() {
                    $('h1, h2').transition({
                        opacity: 1
                    }, 1000, 'ease');
                }, 1000);
            }, 250);
        });
        $('.cover').attr('src', '/cover');

        $('.album').click(function() {
            if (audioplayer.isPaused()) {
                audioplayer.play();
            } else {
                audioplayer.pause();
            }
        });
    }
});
