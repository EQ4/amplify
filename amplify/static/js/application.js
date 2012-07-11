function zeropad(value) {
    var result = value.toString();

    if (value < 10) {
        result = '0' + result;
    }

    return result;
}

function secondsToTime(seconds) {
    return {
        hours: Math.floor(seconds / 60 / 60),
        minutes: Math.floor(seconds / 60 % 60),
        seconds: Math.floor(seconds % 60)
    };
}

var Song = Backbone.Model.extend({
});

var Playlist = Backbone.Collection.extend({
    initialize: function() {
        this.position = 0;
    },
    model: Song,
    url: '/songs',

    getNextTrack: function() {
        var result = false;

        this.position += 1;

        if (this.position < this.models.length) {
            return this.at(this.position);
        } else {
            this.position = 0;

            if (this.get('repeat')) {
                result = this.at(this.position);
            }
        }

        return result;
    },

    getPreviousTrack: function() {
    },
});

var AudioPlayer = Backbone.Model.extend({
    defaults: {
        audio: new Audio(),
        current: {},
        playlist: new Playlist(),
        playing: false,
        repeat: false,
    },

    initialize: function() {
        var audio = this.get('audio');
        var playlist = this.get('playlist');

        playlist.fetch({
            success: _.bind(function(collection, response) {
                var track = collection.first();
                this.set({current: track});
            }, this)
        });

        $(audio).bind('timeupdate', _.bind(function() {
            this.trigger('timeupdate');
        }, this));

        // Advance in the playlist when a song has ended.
        $(audio).bind('ended', _.bind(function() {
            this.next();
        }, this));

        // Update the audio source when the playlist has advanced.
        this.on('change:current', function() {
            var track = this.get('current');
            audio.src = track.get('url');
        }, this);
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
    },

    next: function() {
        var audio = this.get('audio');
        var playlist = this.get('playlist');
        var track = playlist.getNextTrack();

        if (track) {
            this.set({current: track});
            this.play();
        } else {
            this.set({current: playlist.first()});
            this.pause();
        }
    }
});

var ApplicationView = Backbone.View.extend({
    el: 'body',

    initialize: function() {
        var audioplayer = new AudioPlayer();

        // Song changed
        audioplayer.on('change:current', function() {
            var track = this.get('current');
            var title = track.get('title');
            var artist = track.get('artist');

            $('h1').text(title);
            $('h2').text(artist);
            $('head title').text('0:00 | ' + artist + ' - ' + title);

        }, audioplayer);

        // Play/Pause
        audioplayer.on('change:playing', function() {
            var favicon = $('#favicon');
            var vinyl = $('.vinyl');

            if (this.get('playing')) {
                if (!vinyl.hasClass('visible')) {
                    favicon.attr('href', '/static/img/favicon-playing.png');
                    vinyl.addClass('visible');
                }
            } else {
                favicon.attr('href', '/static/img/favicon-paused.png');
                vinyl.removeClass('visible');
            }
        }, audioplayer);

        // Animate the cover when fully loaded
        $('h1, h2').css({opacity: 0});
        $('.cover').load(function() {
            setTimeout(function() {
                $('.album').removeClass('hidden');

                setTimeout(function() {
                    $('h1, h2').transition({
                        delay: 750,
                        opacity: 1
                    }, 1000, 'ease');
                });
            }, 500);
        });
        $('.cover').attr('src', '/cover');

        audioplayer.on('timeupdate', function() {
            var elapsed = secondsToTime(this.get('audio').currentTime);
            var time = elapsed.minutes + ':' + zeropad(elapsed.seconds);
            var track = this.get('current');

            $('head title').text(time + ' | ' + track.get('artist') + ' - ' + track.get('title'));
        });

        $('.album').click(function() {
            if (audioplayer.isPaused()) {
                audioplayer.play();
            } else {
                audioplayer.pause();
            }
        });
    }
});
