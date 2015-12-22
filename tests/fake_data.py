import re
from .test_utils import MockResponse


BRIDGE_CONF = {
    'UTC': '2015-12-21T22:09:34',
    'apiversion': '1.11.0',
    'backup': {'errorcode': 0, 'status': 'idle'},
    'bridgeid': 'something',
    'dhcp': True,
    'factorynew': False,
    'gateway': '192.168.1.1',
    'ipaddress': '192.168.1.2',
    'linkbutton': False,
    'localtime': '2015-12-21T22:09:34',
    'mac': '00:00:00:00:00:00',
    'modelid': 'BSB002',
    'name': 'Hue Bridge',
    'netmask': '255.255.255.0',
    'portalconnection': 'connected',
    'portalservices': True,
    'portalstate': {
        'communication': 'disconnected',
        'incoming': True,
        'outgoing': True,
        'signedon': True
    },
    'proxyaddress': 'none',
    'proxyport': 0,
    'replacesbridgeid': None,
    'swupdate': {
        'checkforupdate': False,
        'devicetypes': {'bridge': True, 'lights': [], 'sensors': []},
        'notify': True,
        'text': 'BSB002 1.11.2 release',
        'updatestate': 2,
        'url': ''
    },
    'swversion': '01029624',
    'timezone': 'Europe/London',
    'whitelist': {
        'token': {
            'create date': '2015-12-14T22:31:31',
            'last use date': '2015-12-14T22:31:31',
            'name': 'test_app'
        },
    },
    'zigbeechannel': 15,
}

BRIDGE_LIGHTS = {
    '1': {
        'manufacturername': 'Philips',
        'modelid': 'LCT007',
        'name': 'Light 1',
        'state': {
            'alert': 'none',
            'bri': 254,
            'colormode': 'hs',
            'ct': 154,
            'effect': 'none',
            'hue': 14678,
            'on': True,
            'reachable': True,
            'sat': 254,
            'xy': [0.5, 0.5]
        },
        'swversion': '66014919',
        'type': 'Extended color light',
        'uniqueid': '00:00:00:00:00:00:00:00-00'
    },
    '2': {
        'manufacturername': 'Philips',
        'modelid': 'LWB006',
        'name': 'Light 2',
        'state': {
            'alert': 'none',
            'bri': 254,
            'on': False,
            'reachable': True
        },
        'swversion': '66015095',
        'type': 'Dimmable light',
        'uniqueid': '00:00:00:00:00:00:00:00-00'
    }
}

BRIDGE_GROUPS = {
    '1': {
        'action': {
            'alert': 'none',
            'bri': 254,
            'colormode': 'hs',
            'ct': 100,
            'effect': 'none',
            'hue': 15910,
            'on': True,
            'sat': 254,
            'xy': [0.4374, 0.4063]
        },
        'lights': ['1'],
        'name': 'Extended Color Lights 1',
        'type': 'LightGroup'
    },
    '2': {
        'action': {
            'alert': 'none',
            'bri': 254,
            'colormode': 'hs',
            'ct': 331,
            'effect': 'none',
            'hue': 15910,
            'on': True,
            'sat': 112,
            'xy': [0.4374, 0.4063]
        },
        'lights': ['2', '1'],
        'name': 'Extended Color Lights 2',
        'type': 'LightGroup'
    },
    '3': {
        'action': {
            'alert': 'none',
            'bri': 254,
            'on': False
        },
        'lights': ['2'],
        'name': 'Dimmer lights',
        'type': 'LightGroup'
    }
}
