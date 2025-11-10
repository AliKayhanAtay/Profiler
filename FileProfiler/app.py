import streamlit as st
import time
import pandas as pd
import os
import uuid
import time
from pathlib import Path
from extractor import get_text
#from ollama import generate
import requests
from prompt import *
import json


model = 'qwen3:8b'
question = 'Is there any personal information in the document ?'

def ask_ollama_old(text, question, model=model):
    resp = requests.post(
        "http://localhost:11434/api/chat",
        json={
            "model": model,
            "messages":[{'role': 'system', 'content': sp, }, 
                        {'role': 'user', 'content': up.format(text, question),}],
            "stream": False,
            'format':"json",
            "options": {"temperature": 0.0,
                        "top_p": 0.9,
                        #"num_predict": 256,   # max tokens to generate
                        #"stop": ["</end>"],   # optional stop tokens
                        },},)    

    r = json.loads(resp.text)
    return r

def ask(text, question, model=model):
    headers = {"Authorization": f"Bearer {os.getenv("OPENROUTER_KEY")}",
               "Content-Type": "application/json",}

    data = {"model": "qwen/qwen3-8b",
            "messages": [{"role": "user", "content": sp},
                         {"role": "user", "content": up.format(text, question)}],}

    r = requests.post(os.getenv("OPENROUTER_URL"),
                    headers=headers, data=json.dumps(data))
    if r.status_code==200:
            print(r.status_code)
            resp = json.loads(r.text.strip())["choices"][0]["message"]["content"]
            return resp
    else:
          print(r.status_code)
          return None

st.set_page_config(page_title="File Profiler", page_icon="🌦️", layout="wide")
title_row = st.container(horizontal=True, vertical_alignment="bottom")
with title_row:
    st.title("File Profiler", anchor=False, width="stretch")

with st.container(border=True):
    example = r'Your path to be scanned > Example "C:\Users\myfolder"'
    path_input = st.text_input(example, value=None, max_chars=None, key='path_input', type="default", 
                               help=None, autocomplete=None, on_change=None, placeholder=None, 
                               disabled=False, label_visibility="visible", icon=None, width="stretch")
    
    options = ['qwen3:8b', 'llama3:8b']
    model_input = st.selectbox('Select your model...', options=options, index=0, key='model_input',
                                help=None, on_change=None, placeholder=None, disabled=False, 
                                label_visibility="visible", accept_new_options=False, width="stretch")

    example = r'Keep it Yes/No > Example: "Is there any personal information in the document ?"'
    question_input = st.text_input(example, value=None, max_chars=None, key='question_input', type="default", 
                               help=None, autocomplete=None, on_change=None, placeholder=None, 
                               disabled=False, label_visibility="visible", icon=None, width="stretch")

c1 = st.session_state["path_input"] is not None
c2 = st.session_state["model_input"] is not None
c3 = st.session_state["question_input"] is not None
if  c1 and c2 and c3:
    directory = Path(path_input)
    rows = []    
    c = 0
    with st.empty():
        for f in directory.iterdir():
            if f.is_file():
                rows.append({
                "Full Path": str(f.resolve()),
                "File Name": f.stem,
                "Extension": f.suffix.lstrip('.')
                })
                c += 1
                st.write(f'File locations are being scanned... {c} files scanned')
                time.sleep(.01)

    df = pd.DataFrame(rows)
    out = pd.DataFrame()
    tt = 0
    with st.spinner('Reading files... Thinking....', show_time=True):
        with st.empty():
            for idx, row in df.iterrows():
                text = get_text(row['Full Path'])
                response = ask(text,
                            st.session_state["question_input"],
                            st.session_state["model_input"])
                try:
                    r_js = json.loads(response)
                    df = pd.DataFrame({k:[v] for k, v in r_js.items()})
                except Exception as e:
                    print(e)
                    df = pd.DataFrame({'raw':[response]})
                    df['Path'] = row['Full Path']

                out = pd.concat([out, df]).reset_index(drop=True)
                st.dataframe(out.tail(5))   
        st.write('List saved... -> data.xlsx')
        df.to_excel('data.xlsx')