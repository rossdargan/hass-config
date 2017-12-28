"""
Standalone code for parsing Hue API data.
Robin Cole. 8-10-2017
"""
import json
import requests

__version__ = 1.2


def load_url(filename):
    """Convenience for loading a url from a json file."""
    try:
        with open(filename, 'r') as fp:
            url = json.load(fp)
    except Exception as e:
        print('Failed to load url')
        url = None
    return url['url']


def load_json_file(filename):
    """Convenience for loading a response data from a json file."""
    try:
        with open(filename, 'r') as fp:
            response = json.load(fp)
    except Exception as e:
        print('Failed to load json file')
        response = None
    return response


def get_response_from_url(url):
    """Returns the Hue API response to a URL as json."""
    response = requests.get(url).json()
    return response


def save_response(response):
    """Convenience to save the json response to file."""
    with open('response.json', 'w') as outfile:
        json.dump(response, outfile)
    return True


def parse_hue_api_response(response):
    """Take in the Hue API json response."""
    data_dict = {}    # The list of sensors, referenced by their hue_id.

    # Loop over all keys (1,2 etc) to identify sensors and get data.
    for key in response.keys():
        sensor = response[key]
        modelid = sensor['modelid'][0:3]
        if modelid in ['RWL', 'SML', 'ZGP']:
            _key = modelid + '_' + sensor['uniqueid'].split(':')[-1][0:5]

            if modelid == 'RWL':
                data_dict[_key] = parse_rwl(sensor)
            elif modelid == 'ZGP':
                data_dict[_key] = parse_zgp(sensor)
            elif modelid == 'SML':
                if _key not in data_dict.keys():
                    data_dict[_key] = parse_sml(sensor)
                else:
                    data_dict[_key].update(parse_sml(sensor))

        elif sensor['modelid'] == 'HA_GEOFENCE':
            data_dict['Geofence'] = parse_geofence(sensor)
    return data_dict


def parse_sml(response):
    """Parse the json for a SML Hue motion sensor and return the data."""
    if response['type'] == "ZLLLightLevel":
        lightlevel = response['state']['lightlevel']
        if lightlevel is not None:
            lux = round(float(10**((lightlevel-1)/10000)), 2)
            dark = response['state']['dark']
            daylight = response['state']['daylight']
            data = {'light_level': lightlevel,
                    'lux': lux,
                    'dark': dark,
                    'daylight': daylight, }
        else:
            data = {'light_level': 'No light level data'}

    elif response['type'] == "ZLLTemperature":
        if response['state']['temperature'] is not None:
            data = {'temperature': response['state']['temperature']/100.0}
        else:
            data = {'temperature': 'No temperature data'}

    elif response['type'] == "ZLLPresence":
        name_raw = response['name']
        arr = name_raw.split()
        arr.insert(-1, 'motion')
        name = ' '.join(arr)
        hue_state = response['state']['presence']
        if hue_state is True:
            state = 'on'
        else:
            state = 'off'

        data = {'model': 'SML',
                'name': name,
                'state': state,
                'battery': response['config']['battery'],
                'last_updated': response['state']['lastupdated'].split('T')}
    return data


def parse_zgp(response):
    """Parse the json response for a ZGPSWITCH Hue Tap."""
    TAP_BUTTONS = {34: '1_click', 16: '2_click', 17: '3_click', 18: '4_click'}
    press = response['state']['buttonevent']
    if press is None:
        button = 'No data'
    else:
        button = TAP_BUTTONS[press]

    data = {'model': 'ZGP',
            'name': response['name'],
            'state': button,
            'last_updated': response['state']['lastupdated'].split('T')}
    return data


def parse_rwl(response):
    """Parse the json response for a RWL Hue remote."""
    press = str(response['state']['buttonevent'])

    if press[-1] in ['0', '2']:
        button = str(press)[0] + '_click'
    else:
        button = str(press)[0] + '_hold'

    data = {'model': 'RWL',
            'name': response['name'],
            'state': button,
            'battery': response['config']['battery'],
            'last_updated': response['state']['lastupdated'].split('T')}
    return data


def parse_geofence(response):
    """Parse the json response for a GEOFENCE and return the data."""
    hue_state = response['state']['presence']
    if hue_state is True:
        state = 'on'
    else:
        state = 'off'
    data = {'name': response['name'],
            'model': 'GEO',
            'state': state}
    return data
