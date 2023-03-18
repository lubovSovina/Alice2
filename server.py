from flask import Flask, request
import logging
import json
import random

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

cities = {
    'москва': ['1652229/ea9cc4be1f014c38ba38',
               '1652229/94b4e970d35ad929f2be'],
    'нью-йорк': ['1533899/c97bc9e215c80d9e90ba',
                 '1533899/b2a77b0ce2e306506f6b'],
    'париж': ["1652229/57de613dd00657e0a6f5",
              '1652229/57978cc71e17b00c8fc4']
}

sessionStorage = {}


@app.route('/post', methods='POST')
def main():
    logging.info(f'Request: {request.json!r}')
    response = {
        'session': request.json['session'],
        'version': request.json['version'],
        'response': {
            'end_session': False
        }
    }
    handle_dialog(response, request.json)
    logging.info(f'Response: {response!r}')
    return json.dumps(response)


def handle_dialog(res, req):
    user_id = req['sesion']['user_id']
    if req['session']['new']:
        res['response']['text'] = 'Привет! Назови своё имя!'
        sessionStorage[user_id] = {
            'first_name': None
        }
        return
    if sessionStorage[user_id]['first_name'] is None:
        first_name = get_first_name(req)
        if first_name is None:
            res['response']['text'] = 'Не расслышала имя. Повтори, пожалуйста!'
        else:
            sessionStorage[user_id]['first_name'] = first_name
            res['response'][
                'text'] = f'Приятно познакомиться, {first_name.title()}. Я - Алиса. Какой город хочешь увидеть?'
            res['response']['buttons'] = [
                {
                    'title': city.title(),
                    'hide': True
                } for city in cities
            ]
    else:
        city = get_city(req)
        if city in cities:
            res['response']['card'] = {
                'type': 'BigImage',
                'title': 'Этот город я знаю.',
                'image_id': random.choice(cities[city])
            }
            res['response']['text'] = 'Я угадал!'
        else:
            res['response']['text'] = 'Первый раз слышу об этом городе. Попробуй ещё разок!'


def get_city(req):
    for en in req['request']['nlu']['entities']:
        if en['type'] == 'YANDEX.GEO':
            return en['value'].get('city', None)


def get_first_name(req):
    for en in req['request']['nlu']['entities']:
        if en['type'] == 'YANDEX.FIO':
            return en['value'].get('first_name', None)


if __name__ == '__main__':
    app.run()
