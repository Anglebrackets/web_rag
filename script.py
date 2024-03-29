"""
web_rag -- RAG from the web -- extention for textgen-webui
Retrieve web data and optionally summarize it, then insert into context.
uses links browser which must be installed.
only tested on linux

TODO:
* ?instead of sending whole query, send from keyword to period, then remove from query.
  Prompt: Research super bowl. When is the super bowl?
   -- "super bowl" sent. prompt is "When is the super bowl".
* "Research" key: saves to string in params,
  "Analyse" key: summarizes, then saves
  "Examine" key: doesnt save query, doesn't use saved string, only puts results in context
  "Scan" key: like Examine, but summarized
  "Summarize" key: like Get, but summarized
  
* summarize: use chat.generate_chat_prompt on "summarize the following:"+ query-results
  before storing in research string
* button array for multiple keyword/url pairs

WIP:

DONE:
*  "Get" key: followed by url(s). saves to context.
   prompt: Get https://www.wikipedia.org/wiki/Charles_Martel 
  Put results in saved string (editable!), then always added to context until cleared
  Results of multiple requests accumulate in string until cleared.
* Clear Research button
* use substitution variable for query in url instead of adding at end
"""

import gradio as gr
import pickle
from modules import chat, shared
from modules.chat import generate_chat_prompt
import os
import urllib.parse


try:
    with open('web_rag_data.pkl', 'rb') as f:
        params = pickle.load(f)
except FileNotFoundError:
    params = {
        "display_name": "Web RAG",
        "activate": False,
        "get_key":  "get",
        "url":      "https://lite.duckduckgo.com/lite/?q=%q",
        "start":    "[ Next Page > ]",
        "end":      "\n6.   ",
        "max":      "5000",
        "auto_key": "web,",
        "data":     "",
    }
params.update({
        "get_key":  "get",
        "auto_key": "web,",
})
def get_search_context(url, query):
    if len(query) > 0:
        print(f"query={query}")
        query = urllib.parse.quote_plus(query)
        if url.find('%q') >= 0:
            url = url.replace('%q', query)
    print(f"get_search_context: url={url}")
    #search_context = "\nJonn Jonze is the president of Frubaz Corp.\n"
    search_context = os.popen('links -dump ' + url).read()
    if len(params['start']) > 0:
        start = search_context.find(params['start'])
        if start < 0:
            start = 0
        else:
            start = start + 15
        search_context = search_context[start:]
    if len(params['end']) > 0:
        end = search_context.find(params['end'])
        if end < 0:
            end = int(params['max'])
    else:
        end = int(params['max'])
    search_context = search_context[:end]
    return search_context

def save():
    with open('web_rag_data.pkl', 'wb') as f:
        pickle.dump(params, f)

def custom_generate_chat_prompt(user_input, state, **kwargs):
    """
    Only used in chat mode.
    """
    user_prompt = user_input
    if params['activate']:
        retrieved = ""
        parts = user_prompt.split(" ", 1)
        if len(parts) > 1:
            key = parts[0]
            if key.lower() == params['auto_key'].lower():
                user_prompt = parts[1].strip()
                retrieved = get_search_context(params['url'], user_prompt)
            elif key.lower() == params['get_key'].lower():  # url in prompt
                url = parts[1].strip()
                retrieved = get_search_context(url, "")
                total = len(retrieved) + len(params['data'])
                user_prompt = f'Say "Retrieved {len(retrieved)} characters." and "Total is {total}".'
        data = params['data'] + retrieved
        if len(retrieved) > 0:
            print(f"Retrieved {len(retrieved)}, total:{len(data)}")
            params.update({'data': data})
            save()
        context = data + state['context']
        state.update({'context': context})
    result = chat.generate_chat_prompt(user_prompt, state, **kwargs)
    return result

def ui():
    """
    Gets executed when the UI is drawn. Custom gradio elements and
    their corresponding event handlers should be defined here.

    To learn about gradio components, check out the docs:
    https://gradio.app/docs/
    """
    with gr.Accordion("Web Retrieval-Augmented Generation - Retrieve data from web pages and insert into context", open=True):
        activate = gr.Checkbox(value=params['activate'], label='Activate Web RAG')
        with gr.Accordion("Enter one of these keys at the beginning of the prompt (not case sensitive). Retrieved data is accumulated and inserted into the context of all following prompts, until the 'Clear Data' button is pressed.", open=True):
            with gr.Row():
                with gr.Column():
                    key = gr.Textbox(value=params['auto_key'], label="AUTO: Key text at start of prompt that invokes Auto-RAG. Not case-sensitive. When invoked, the remainder of the prompt is inserted into the url template below, results retrieved and then the prompt is processed normally with the retrieved context.")
                    url = gr.Textbox(value=params['url'], label='URL template: url-encoded prompt will replace %q')
                get_key = gr.Textbox(value=params['get_key'], label="DIRECT: Key text at start of prompt that invokes direct page retrieval.  The url to retrieve must follow this key in the prompt.")
        with gr.Row():
            start = gr.Textbox(value=params['start'], label='Start: Retrieved data capture starts after this text is found (starts at beginning if not found)')
            end = gr.Textbox(value=params['end'], label='End: Retrieved data capture ends when this text is found (overrides maximum characters if found)')
            maxchars = gr.Number(value=params['max'], label='Maximum characters of retrieved data to keep (if end text not found)')
        with gr.Accordion("Edit retrieved data", open=True):
            with gr.Row():
                edit = gr.Button("Show Data", elem_classes='refresh-button')
                clear = gr.Button("Clear Data", elem_classes='refresh-button')
            retrieved = gr.Textbox(value=params['data'], label='Retrieved data')

    def update_activate(x):
        params.update({'activate': x})
        save()
    def update_get_key(x):
        params.update({'get_key': x})
        save()
    def update_maxchars(x):
        params.update({'max': x})
        save()
    def update_start(x):
        params.update({'start': x})
        save()
    def update_end(x):
        params.update({'end': x})
        save()
    def update_url(x):
        params.update({'url': x})
        save()
    def update_key(x):
        params.update({'auto_key': x})
        save()
    def clear_clicked(button_input):
        params.update({'data': ""})
        save()
        return ""
    def edit_clicked(button_input):
        data = params['data']
        return data
    def update_retrieved(x):
        params.update({'data': x})
        save()

    activate.change(update_activate, activate, None)
    get_key.change(update_get_key, get_key, None)
    url.change(update_url, url, None)
    maxchars.change(update_maxchars, maxchars, None)
    key.change(update_key, key, None)
    start.change(update_start, start, None)
    end.change(update_end, end, None)
    clear.click(clear_clicked, clear, retrieved)
    edit.click(edit_clicked, edit, retrieved)
    retrieved.change(update_retrieved, retrieved, None)
