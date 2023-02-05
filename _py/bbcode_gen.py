from configparser import ConfigParser
import requests

base_url = 'https://osu.ppy.sh/api/v2'
auth_url = 'https://osu.ppy.sh/oauth/token'

def api_usable(config: ConfigParser) -> bool:
    print('Testing API Usable...')
    return str(config['API']['ClientID']).lower() != 'none' and str(config['API']['ClientSecret']).lower() != 'none'

def api_test_connect(config: ConfigParser) -> dict | bool:
    print('Testing API Connection...')
    
    cid = config['API']['ClientID']
    csc = config['API']['ClientSecret']
    
    response = requests.post(f'{auth_url}', json={
        'client_id': cid,
        'client_secret': csc,
        'grant_type': 'client_credentials',
        'scope': 'public'
    })
    
    if response.status_code >= 200 and response.status_code <= 203:
        return response.json()
    else:
        return False
    
def request_user_beatmapset(config: ConfigParser) -> str:
    if get_allow(config['Input'], 'AllowURLAsInput'):
        req = input('Beatmap (ID / URL) : ')
        if '/' in req:
            parts = req.split('/')
            for part in parts:
                if '#' in part:
                    return part.split('#')[0]
        else:
            if req.isnumeric():
                return req
            else:
                raise Exception('Value not valid URL or Beatmap ID!')
    else:
        req = input('Beatmap (ID) : ')
        if '/' in req:
            input('Please Configure "Input > AllowURLAsInput" in bbconfig.ini to use URL\'s ...')
            exit()
        else:
            if req.isnumeric():
                return req
            else:
                raise Exception('Value not valid URL or Beatmap ID!')

def construct_image_bbcode(mode: str, sr: float) -> str:
    match mode:
        case 0: mode = 'std'
        case 1: mode = 'taiko'
        case 2: mode = 'ctb'
        case 3: mode = 'mania'
        case _: mode = 'unknown'
        
    return f'[img]https://raw.githubusercontent.com/hiderikzki/osu-difficulty-icons/main/rendered/{mode}/stars_{sr}.png[/img]';

def get_tag(tag: str, category: str, field: str, close: bool) -> str:
    return '[{}{}]'.format('/' if close else '', tag) if get_allow(config[category], field) else ''

get_allow = lambda selection, field : True if int(selection[field]) == 1 else False

config = ConfigParser()
config.read('bbconfig.ini')

if not api_usable(config):
    input('Please Configure API in bbconfig.ini before use ... ')
    exit()
    
print('Ok.\n')

connection = api_test_connect(config)    

if not connection:
    input('Please Reconfigure API in bbconfig.ini before use, invalid data ... ')
    exit()
    
print('Ok.\n')

token = connection['access_token']

request_headers = {
    'Authorization': f'Bearer {token}'
}

beatmapset = request_user_beatmapset(config)
beatmapset_request = requests.request('GET', f'{base_url}/beatmapsets/{beatmapset}', headers=request_headers)


difficulties = beatmapset_request.json()['beatmaps']

title_color = config['Colors']['TitleColor']

bbcode_storage = {
    0: [],
    1: [],
    2: [],
    3: []
}

for difficulty in difficulties:
    mode = int(difficulty['mode_int'])
    sr = round(float(difficulty['difficulty_rating']), 1)
    bbcode_storage[mode].append([construct_image_bbcode(mode, sr), difficulty['version'], sr])

for mode in bbcode_storage:
    match mode:
        case 0: mode_name = 'Standard'
        case 1: mode_name = 'Taiko'
        case 2: mode_name = 'CTB'
        case 3: mode_name = 'Mania'
        
    if len(bbcode_storage[mode]) != 0:
        print(f'\nBBCode Difficulty Listing for {mode_name}')
        print('{}{}[color=#{}][heading]Difficulties[/color][/heading]'.format(get_tag('notice', 'Formatting', 'SurroundWithBox', False), get_tag('centre', 'Formatting', 'CentreContent', False), title_color))
        
        for bbcode in sorted(bbcode_storage[mode], key = lambda item : item[2]):
            if get_allow(config['Formatting'], 'AddSRToDifficulties'):
                print(f'{bbcode[0]} {bbcode[1]} - {bbcode[2]}*')
            else:
                print(f'{bbcode[0]} {bbcode[1]}')
        
        print('{}{}'.format(get_tag('centre', 'Formatting', 'CentreContent', True), get_tag('notice', 'Formatting', 'SurroundWithBox', True)))