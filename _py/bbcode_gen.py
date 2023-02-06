from configparser import ConfigParser
import requests
import json
import ast

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

def request_saved_color_data() -> dict:
    color_data = requests.request('GET', 'https://raw.githubusercontent.com/hiderikzki/osu-difficulty-icons/main/rendered/color_data.txt')
    return ast.literal_eval(color_data.text)

colors = request_saved_color_data()

get_allow = lambda selection, field : True if int(selection[field]) == 1 else False
rgb_to_hex = lambda rgb : '%02x%02x%02x' % rgb[0:3]

def fancy_color_sr(sr, round_sr) -> str:
    color = colors[float(round_sr)]
    
    r = min(color[0] + 25, 255)
    g = min(color[1] + 25, 255)
    b = min(color[2] + 25, 255)
    
    return ' - [color=#{}]{}[/color][color=#FCFF5A]*[/color]'.format(rgb_to_hex((r, g, b, 255)) 
                                                                     if get_allow(config['Colors'], 'FancySRColoring') 
                                                                     else 'FFFFFF', 
                                                                     sr) if get_allow(config['Formatting'], 'AddSRToDifficulties') else ''

def user_link(config: ConfigParser, uid, name):
    if get_allow(config['Formatting'], 'IgnoreSelf') and int(config['UserID']) == int(uid):
        return ''
    return ' by [b]{}[/b]'.format('[color=#CFCFCF]Me[/color]' 
                                  if name == '' else 
                                  '[url=https://osu.ppy.sh/users/{}]{}[/url]'.format(uid, name) 
                                  if get_allow(config['Formatting'], 'LinkMappers') else 
                                  name) if get_allow(config['Formatting'], 'DisplayMappers') else ''
    

config = ConfigParser()
config.read('bbconfig.ini')

if int(config['API']['UserID']) <= 0:
    input('Please Configure UserID in bbconfig.ini before use ... ')
    exit()

if not api_usable(config):
    input('Please Configure ClientID & ClientSecret in bbconfig.ini before use ... ')
    exit()
    
print('Ok.\n')

connection = api_test_connect(config)    

if not connection:
    input('Please Reconfigure ClientID & ClientSecret in bbconfig.ini before use, invalid data ... ')
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
    unrounded_sr = float(difficulty['difficulty_rating'])
    sr = round(unrounded_sr, 1)
    self_id = config['API']['UserID']
    
    if int(self_id) != int(difficulty['user_id']):
        target_id = difficulty['user_id']
        request_user = requests.request('GET', f'{base_url}/users/{target_id}', headers=request_headers)
        bbcode_storage[mode].append([construct_image_bbcode(mode, sr), 
                                     difficulty['version'], 
                                     sr, 
                                     unrounded_sr, 
                                     difficulty['user_id'], 
                                     request_user.json()['username']])
    else:
        bbcode_storage[mode].append([construct_image_bbcode(mode, sr), 
                                     difficulty['version'], 
                                     sr, 
                                     unrounded_sr, 
                                     difficulty['user_id'], 
                                     ''])

for mode in bbcode_storage:
    match mode:
        case 0: mode_name = 'Standard'
        case 1: mode_name = 'Taiko'
        case 2: mode_name = 'CTB'
        case 3: mode_name = 'Mania'
        
    if len(bbcode_storage[mode]) != 0:
        print(f'\nBBCode Difficulty Listing for {mode_name}')
        print('{}{}[heading][color=#{}]Difficulties[/color][/heading]'.format(get_tag('notice', 'Formatting', 'SurroundWithBox', False), 
                                                                              get_tag('centre', 'Formatting', 'CentreContent', False), title_color))
        
        for bbcode in sorted(bbcode_storage[mode], key = lambda item : item[2]):
            print('{} {}{}{}{}{}'.format(bbcode[0], 
                                 get_tag('color', 'Colors', 'MatchIconColorToDifficulty', False).replace('[color]', '[color=#{}]'.format(rgb_to_hex(colors[bbcode[2]]))),
                                 bbcode[1],
                                 get_tag('color', 'Colors', 'MatchIconColorToDifficulty', True), 
                                 fancy_color_sr(bbcode[3], bbcode[2]),
                                 user_link(config, bbcode[4], bbcode[5])))
        
        print('{}{}'.format(get_tag('centre', 'Formatting', 'CentreContent', True), 
                            get_tag('notice', 'Formatting', 'SurroundWithBox', True)))