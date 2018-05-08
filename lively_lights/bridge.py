#! /usr/bin/env python3

from flask import Flask, jsonify, request
app = Flask(__name__)

@app.route('/api/username/lights/1', methods=['GET'])
def get_light():

    state = {
        'state': {
            'on': True,
            'bri': 190,
            'hue': 31927,
            'sat': 254,
            'effect': 'none',
            'xy': [
                0.4116,
                0.5161
            ],
            'ct': 293,
            'alert': 'none',
            'colormode': 'hs',
            'reachable': True
        },
        'type': 'Extended color light',
        'name': 'Wohnzimmerschrank links',
        'modelid': 'LCT001',
        'manufacturername': 'Philips',
        'uniqueid': '00:17:88:01:00:be:64:99-0b',
        'swversion': '5.23.1.13452'
    }

    return jsonify(state)


if __name__ == '__main__':
    app.run(debug=True, port=8080)
