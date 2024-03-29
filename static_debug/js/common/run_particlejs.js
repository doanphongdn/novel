particlesJS('particles-js', {
    'particles': {
        'number': {'value': 50},
        'color': {'value': '#333'},
        'shape': {'type': 'triangle', 'polygon': {'nb_sides': 5}},
        'opacity': {'value': 0.06, 'random': false},
        'size': {'value': 11, 'random': true},
        'line_linked': {'enable': true, 'distance': 150, 'color': '#333', 'opacity': 0.4, 'width': 1},
        'move': {
            'enable': true,
            'speed': 4,
            'direction': 'none',
            'random': false,
            'straight': false,
            'out_mode': 'out',
            'bounce': false
        }
    },
    'interactivity': {
        'detect_on': 'canvas',
        'events': {'onhover': {'enable': false}, 'onclick': {'enable': true, 'mode': 'push'}, 'resize': true},
        'modes': {'push': {'particles_nb': 4}}
    },
    'retina_detect': true
}, function () {
});