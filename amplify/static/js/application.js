var AudioPlayer = Backbone.Model.extend({
    defaults: {
        audio: new Audio(),
        playlist: [],
        playlistPosition: 0,
        current: {},
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
        return this.get('audio').paused;
    },

    play: function() {
        var audio = this.get('audio');
        audio.play();
    },

    pause: function() {
        this.get('audio').pause();
    }
});

var ApplicationView = Backbone.View.extend({
    el: 'body',

    initialize: function() {
        var audioplayer = new AudioPlayer();

        audioplayer.on('change:current', function() {
            var current = this.get('current');

            $('h1').text(current.title);
            $('h2').text(current.artist);
            $('head title').text(current.artist + ' - ' + current.title);

        }, audioplayer);

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

                $('.vinyl')
                .css({
                    rotate: '-90deg'
                })
                .transition({
                    marginTop: '-50px',
                    rotate: '0deg'
                }, 500);
            } else {
                audioplayer.pause();

                $('.vinyl')
                .transition({
                    marginTop: '0',
                    rotate: '-90deg'
                }, 500)
                .css({
                    rotate: '0deg'
                });
            }
        });
    }
});
