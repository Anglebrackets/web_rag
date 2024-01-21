"""
An example of extension. It does nothing, but you can add transformations
before the return statements to customize the webui behavior.

Starting from history_modifier and ending in output_modifier, the
functions are declared in the same order that they are called at
generation time.
"""

import gradio as gr
import pickle
from modules import chat, shared
#from modules.extensions import apply_extensions
#from modules.text_generation import encode, get_max_prompt_length
from modules.chat import generate_chat_prompt
import os
import urllib.parse


try:
    with open('saved_data.pkl', 'rb') as f:
        params = pickle.load(f)
except FileNotFoundError:
    params = {
        "display_name": "Web RAG",
        "url": "https://www.duckduckgo.com/?q=",
        "activate": False,
    }

def get_search_context(url, query):
    query = urllib.parse.quote_plus(query)
    print(f"get_search_context: {url} + {query}")
    search_context = os.popen('links -dump ' + url + query).read()
    start = search_context.find("[ Next Page > ]")
    if start < 0:
      start = 0
    else:
      start = start + 15
    search_context = search_context[start:]
    end = search_context.find("\n4.   ")
    if end < 0:
      end = 3000
    search_context = search_context[:end]
    #print(f"search_context:{search_context}")
    return search_context

def custom_generate_chat_prompt(user_input, state, **kwargs):
    """
    Only used in chat mode.
    """
    user_prompt = user_input
    if params['activate']:
        if user_prompt.startswith('www,'):
            user_prompt = user_input[4:].strip()
            #search_context = "\nJonn Jonze is the president of Frubaz Corp.\n"
            search_context = get_search_context(params['url'], user_prompt)
            state['context'] = search_context + state['context']
    result = chat.generate_chat_prompt(user_prompt, state, **kwargs)
    return result


def ui():
    """
    Gets executed when the UI is drawn. Custom gradio elements and
    their corresponding event handlers should be defined here.

    To learn about gradio components, check out the docs:
    https://gradio.app/docs/
    """
    activate = gr.Checkbox(value=params['activate'], label='Activate Web RAG')
    url = gr.Textbox(value=params['url'], label='Search URL')

    def update_activate(x):
        params.update({'activate': x})
        with open('saved_data.pkl', 'wb') as f:
            pickle.dump(params, f)

    def update_url(x):
        params.update({'url': x})
        with open('saved_data.pkl', 'wb') as f:
            pickle.dump(params, f)

    activate.change(update_activate, activate, None)
    url.change(update_url, url, None)
