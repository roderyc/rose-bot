from flask import Flask, request
import os
import requests
import json

app = Flask(__name__)

BEGINNING = 'BEGINNING'
ASKED = 'ASKED'
CONFUSED = 'CONFUSED'
SATISFIED = 'SATISFIED'

HIGH_CLASS_ROSE_LINK = 'https://drizly.com/meiomi-rose/p61784'
BRO_ROSE_LINK = 'https://drizly.com/charles-and-charles-rose/p2516'
BASIC_ROSE_LINK = 'https://drizly.com/white-girl-rose/p20394'

INITIAL_BODY = u'''<p>Well hello there, it sounds like you're thirsty as hell and in need of a refreshing drink. Might I interest you in a ros\xe9?</p>
<p>I've quite a selection, but how about you tell me a little about yourself so I can refer you to the proper drink?</p>
<p>Are you currently on a yacht or feel you deserve to be?</p>
<p>Going out with the bros and got no time for masculo-normative bullshit?</p>
<p>You a basic white girl?</p>
'''

BOAT_RESPONSE = 'I\'m on a boat'
BRO_RESPONSE = 'BRO'
BASIC_RESPONSE = 'Basic AF'
NONE_RESPONSE = '... None of these'
REALLY_NONE_RESPONSE = 'Yes, really none of these'

def button(response):
    return {'value': response, 'label': response}

INITIAL_RESPONSE_BUTTONS = [button(BOAT_RESPONSE), button(BRO_RESPONSE), button(BASIC_RESPONSE), button(NONE_RESPONSE)]
CONFUSED_RESPONSE_BUTTONS = [button(BOAT_RESPONSE), button(BRO_RESPONSE), button(BASIC_RESPONSE), button(REALLY_NONE_RESPONSE)]

CONVERSATIONS = {}

API_HOST = os.environ.get('API_HOST')
MESSAGE_ENDPOINT_FORMAT = API_HOST + "/open/conversations/%s/messages"

AUTH_TOKEN = os.environ.get('AUTH_TOKEN')
AUTH = 'bearer %s' % AUTH_TOKEN

def post_message(conversationId, message):
    r = requests.post(MESSAGE_ENDPOINT_FORMAT % conversationId, json=message, headers={'Authorization': AUTH})
    r.raise_for_status()

def make_message(orgId, body, type, buttons=[]):
    return {'orgId': orgId, 'body': body, 'type': type, 'buttons': buttons}

def respond_to_probable_button_response(conversationId, orgId, body):
    if body == BOAT_RESPONSE:
        post_message(conversationId, make_message(orgId, 'This should satisfy you, bourgeois animal ' + HIGH_CLASS_ROSE_LINK, 'chat'))
        return SATISFIED
    elif body == BRO_RESPONSE:
        post_message(conversationId, make_message(orgId, 'BROOOOOOO ' + BRO_ROSE_LINK, 'chat'))
        return SATISFIED
    elif body == BASIC_RESPONSE:
        post_message(conversationId, make_message(orgId, 'How you go girl ' + BASIC_ROSE_LINK, 'chat'))
        return SATISFIED
    elif body == NONE_RESPONSE:
        post_message(conversationId, make_message(orgId, 'Ughh.. what? Wait, are you sure?', 'chat', CONFUSED_RESPONSE_BUTTONS))
        return CONFUSED
    elif body == REALLY_NONE_RESPONSE:
        post_message(conversationId, make_message(orgId, '??? Ok...', 'chat'))
        return SATISFIED
    else:
        post_message(conversationId, make_message(orgId, 'Sssshhhh sshhhhh, don\'t fight it, just answer', 'chat', INITIAL_RESPONSE_BUTTONS))
        return ASKED

def handle_state_edge(state, orgId, message):
    conversationId = message.get('conversationId')
    body = message.get('body')

    if state == BEGINNING:
        post_message(conversationId, make_message(orgId, INITIAL_BODY, 'chat', INITIAL_RESPONSE_BUTTONS))
        return ASKED
    if state == ASKED:
        return respond_to_probable_button_response(conversationId, orgId, body)
    elif state == CONFUSED:
        return respond_to_probable_button_response(conversationId, orgId, body)
    elif state == SATISFIED:
        return state

@app.route('/', methods=['POST'])
def accept_message():
    event = request.get_json()    
    if event and event.get('type') == 'new-message':
        orgId = event.get('orgId')
        message = event.get('data')
        conversationId = message.get('conversationId')
        if (CONVERSATIONS.has_key(conversationId)):
            state = CONVERSATIONS[conversationId]
            CONVERSATIONS[conversationId] = handle_state_edge(state, orgId, message)
        elif ('rose' in message.get('body').lower() and
              'contact' == message.get('author').get('type')):
            CONVERSATIONS[conversationId] = handle_state_edge(BEGINNING, orgId, message)
    return json.dumps(CONVERSATIONS)

if __name__ == "__main__":
    app.run()
