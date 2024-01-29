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
    with open('saved_data.pkl', 'rb') as f:
        params = pickle.load(f)
except FileNotFoundError:
    params = {
        "display_name": "Web RAG",
        "activate": False,
        "url":      "https://lite.duckduckgo.com/lite/?q=%q",
        "start":    "[ Next Page > ]",
        "end":      "\n6.   ",
        "space":    "",
        "max":      "5000",
        "key":      "web,",
        "data":     "",
    }
def get_search_context(url, query):
    if len(query) > 0:
        print(f"query={query}")
        query = urllib.parse.quote_plus(query)
        if len(params['space']) > 0:
            query = query.replace("+", params['space'])
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
    print(f"search_context:\n{search_context}")
    return search_context

def save():
    with open('saved_data.pkl', 'wb') as f:
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
            if key.lower() == params['key'].lower():
                user_prompt = parts[1].strip()
                retrieved = get_search_context(params['url'], user_prompt)
            elif key.lower() == "get":  # url in prompt
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
    with gr.Accordion("Web RAG -- Retrieval-Augmented Generation using web content"):
        with gr.Row():
            activate = gr.Checkbox(value=params['activate'], label='Activate Web RAG')
            maxchars = gr.Number(value=params['max'], label='Maximum characters of retrieved data to keep')
        with gr.Row():
            start = gr.Textbox(value=params['start'], label='Start: Retrieved data capture starts after this text is found')
            end = gr.Textbox(value=params['end'], label='End: Retrieved data capture ends when this text is found (overrides max chars if found)')
        with gr.Accordion("Auto-RAG parameters", open=False):
            url = gr.Textbox(value=params['url'], label='Retrieval URL')
            with gr.Row():
                key = gr.Textbox(value=params['key'], label="Key: Text at start of prompt to invoke RAG")
                space = gr.Textbox(value=params['space'], label="Space: After URL-encoding the query, substitute this for '+'")
        with gr.Accordion("Edit retrieved data", open=False):
            with gr.Row():
                edit = gr.Button("Show Data", elem_classes='refresh-button')
                clear = gr.Button("Clear Data", elem_classes='refresh-button')
            retrieved = gr.Textbox(value=params['data'], label='Retrieved data')

    def update_activate(x):
        params.update({'activate': x})
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
        params.update({'key': x})
        save()
    def update_space(x):
        params.update({'space': x})
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
    url.change(update_url, url, None)
    maxchars.change(update_maxchars, maxchars, None)
    key.change(update_key, key, None)
    start.change(update_start, start, None)
    end.change(update_end, end, None)
    space.change(update_space, space, None)
    clear.click(clear_clicked, clear, retrieved)
    edit.click(edit_clicked, edit, retrieved)
    retrieved.change(update_retrieved, retrieved, None)
