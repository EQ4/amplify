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

    step: function(delta) {
        var result = false;

        this.position += delta;

        if (this.position < 0) {
            this.position = 0;
        } else if (this.position > this.models.length - 1) {
            this.position = this.models.length - 1;
        } else {
            // We're within range
            result = this.at(this.position);
        }

        return result;
    },

    getNextTrack: function() {
        var track = this.step(1);

        if (!track && this.get('repeat')) {
            this.position = 0;
            track = this.at(this.position);
        }

        return track;
    },

    getPreviousTrack: function() {
        var track = this.step(-1);

        if (!track && this.get('repeat')) {
            this.position = this.models.length;
            track = this.at(this.position);
        }

        return track;
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
            playlist.position = 0;
            this.set({current: playlist.first()});
            this.pause();
        }
    },

    previous: function() {
        var audio = this.get('audio');
        var playlist = this.get('playlist');
        var track = playlist.getPreviousTrack();

        if (track) {
            this.set({current: track});
            this.play();
        } else {
            // No previous track, trigger the change event to reload the
            // first track in the playlist.
            this.trigger('change:current');
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

        $('.cover').click(function() {
            if (audioplayer.isPaused()) {
                audioplayer.play();
            } else {
                audioplayer.pause();
            }
        });

        $('#previous').click(function(e) {
            e.preventDefault();
            audioplayer.previous();
        });

        $('#next').click(function(e) {
            e.preventDefault();
            audioplayer.next();
        });
    }
});
