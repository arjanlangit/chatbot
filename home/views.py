import json, requests, random, re
from pprint import pprint

from django.views import generic
from django.http.response import HttpResponse

from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

from django.utils.datastructures import MultiValueDictKeyError
from PyDictionary import PyDictionary


# Create your views here.


PAGE_ACCESS_TOKEN = 'EAACZCtHKZBGAwBABQCNNS9KEZADQm0ZC5NlcHIzhWvGXI5xdrWoDY76xZAH7UNTzlzQqm10OuOdHC8YIkZAFnPyLdShYB2ZBtBFNTwr6Fb5KpTSBn3wxs9YvFE8zQqF7tpgdrGiaRLRBhDOyTazkwIOa2jAfGIKIbZA4ht3Ka2o1VAZDZD'
VERIFY_TOKEN = '122118'

chats = {
        'hello': ["""Hello and Welcome to Heaven Chatbot """,
                  """Welcome! """],
        'define': 'No definitions found for this word!',
        }



def post_facebook_message(fbid, recevied_message):
    # Remove all punctuations, lower case the text and split it based on space
    tokens = re.sub(r"[^a-zA-Z0-9\s]",' ',recevied_message).lower().split()
    reply = ''
    word = ''

    if 'define' in tokens and len(tokens) == 2:
        # Start PyDictionary
        dictionary = PyDictionary()
        # The word need to be defined
        word = tokens[1]
        # Get meaning of the word
        meaning = dictionary.meaning(word)
        nouns = meaning['Noun']
        # verbs = meaning['Verb']
        # Store the meaning of the word
        chats['define'] = nouns
        # Return a reply about the word
        reply = "{} means:".format(word)
        for noun in range(3):
            reply = "{}\n- {}".format(reply, nouns[noun].capitalize())

    elif not reply:
        reply = "I didn't understand! Send 'hello' to receive a reply" 
        
    else:
        for token in tokens:
            if token in chats:
                reply = random.choice(chats[token])
                break

    user_details_url = "https://graph.facebook.com/v2.6/%s"%fbid 
    user_details_params = {'fields':'first_name,last_name,profile_pic', 'access_token':PAGE_ACCESS_TOKEN} 
    user_details = requests.get(user_details_url, user_details_params).json() 

    reply = 'Hello {}\n{}\n'.format(user_details['first_name'], reply)
    # reply = 'Hello '+user_details['first_name']+'! ' + reply
                   
    post_message_url = 'https://graph.facebook.com/v2.6/me/messages?access_token=%s'%PAGE_ACCESS_TOKEN
    response_msg = json.dumps({"recipient":{"id":fbid}, "message":{"text":reply}})
    status = requests.post(post_message_url, headers={"Content-Type": "application/json"},data=response_msg)

class ChatbotView(generic.View):
    def get(self, request, *args, **kwargs):
        token = self.request.GET['hub.verify_token']
        challenge = self.request.GET['hub.challenge']

        if token == VERIFY_TOKEN:
            return HttpResponse(challenge)
        else:
            return HttpResponse('Error, invalid token')
        return HttpResponse('400')

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return generic.View.dispatch(self, request, *args, **kwargs)

    # Post function to handle Facebook messages
    def post(self, request, *args, **kwargs):
        # Converts the text payload into a python dictionary
        incoming_message = json.loads(self.request.body.decode('utf-8'))
        # Facebook recommends going through every entry since they might send
        # multiple messages in a single call during high load
        for entry in incoming_message['entry']:
            for message in entry['messaging']:
                # Check to make sure the received call is a message call
                # This might be delivery, optin, postback for other events 
                if 'message' in message:
                    # Print the message to the terminal
                    pprint(message)
                    post_facebook_message(message['sender']['id'], message['message']['text'])    

        return HttpResponse('200')