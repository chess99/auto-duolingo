
import requests


def get_headers():
    headers = {
        'accept': 'application/json; charset=UTF-8',
        'accept-language': 'en',
        'authorization': 'Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJleHAiOjYzMDcyMDAwMDAsImlhdCI6MCwic3ViIjoxNDkzNDA3MDAxfQ.DJ_KsiSgJd63qBgyLS_8lB6ZHb5ERnkuvabXl0pB7N8',
        'cache-control': 'no-cache',
        'content-type': 'application/json; charset=UTF-8',
        'dnt': '1',
        'origin': 'https://www.duolingo.cn',
        'pragma': 'no-cache',
        'referer': 'https://www.duolingo.cn/lesson',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'user-agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1',
        'x-amzn-trace-id': 'User=1493407001',
        'x-requested-with': 'XMLHttpRequest'
    }
    return headers


def get_challenge_types():
    challenge_types = ["assist", "characterIntro", "characterMatch", "characterPuzzle", "characterSelect", "characterTrace", "characterWrite", "completeReverseTranslation", "definition", "dialogue", "extendedMatch", "extendedListenMatch", "form", "freeResponse", "gapFill", "judge", "listen", "listenComplete", "listenMatch", "match", "name", "listenComprehension", "listenIsolation", "listenSpeak", "listenTap", "orderTapComplete", "partialListen", "partialReverseTranslate", "patternTapComplete",
                       "radioBinary", "radioImageSelect", "radioListenMatch", "radioListenRecognize", "radioSelect", "readComprehension", "reverseAssist", "sameDifferent", "select", "selectPronunciation", "selectTranscription", "svgPuzzle", "syllableTap", "syllableListenTap", "speak", "tapCloze", "tapClozeTable", "tapComplete", "tapCompleteTable", "tapDescribe", "translate", "transliterate", "transliterationAssist", "typeCloze", "typeClozeTable", "typeComplete", "typeCompleteTable", "writeComprehension"]
    return challenge_types


def fetch_session(params):
    url = 'https://www.duolingo.cn/2017-06-30/sessions'
    headers = get_headers()
    data = {
        "challengeTypes": get_challenge_types(),
        "fromLanguage": "zh",
        "isFinalLevel": False,
        "isV2": True,
        "juicy": True,
        "learningLanguage": "ja",
        "isCustomIntroSkill": False,
        "isGrammarSkill": False,
        "showGrammarSkillSplash": False,
        "pathExperiments": ["UNIT_VISION_BB_93"],
        "type": params['type'],
        "levelIndex": params['levelIndex'],
        "levelSessionIndex": params['levelSessionIndex'],
    }

    if 'skillId' in params:
        data['skillId'] = params['skillId']
    elif 'skillIds' in params:
        data['skillIds'] = params['skillIds']

    response = requests.post(url, headers=headers, json=data)
    return response
