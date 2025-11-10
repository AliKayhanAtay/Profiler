import streamlit as st
import pandas as pd
import os
from pathlib import Path
from extractor import get_text
from prompt import ask
import json

question = 'Is there any personal information in the document ?'

st.set_page_config(page_title="File Profiler", page_icon="🌦️", layout="wide")
title_row = st.container(horizontal=True, vertical_alignment="bottom")
with title_row:
    st.title("File Profiler", anchor=False, width="stretch")

with st.container(border=True):
    example = r'Your path to be scanned > Example "C:\Users\myfolder"'
    path_input = st.text_input(example, value=None, max_chars=None, key='path_input', type="default", 
                               help=None, autocomplete=None, on_change=None, placeholder=None, 
                               disabled=False, label_visibility="visible", icon=None, width="stretch")
    
    options = ['qwen/qwen3-8b', 'llama3:8b']
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
        rows = []    
        c = 0
        for current_root, dirs, files in os.walk(path_input):
            for name in files:
                f = Path(os.path.join(current_root, name))
                rows.append({
                "Full Path": f,
                "File Name": f.stem,
                "Extension": f.suffix.lstrip('.')
                })
                c += 1
                st.write(f'Scanning... {c} files found') 
        if len(rows)==0:
            st.stop()


    df = pd.DataFrame(rows)
    out = pd.DataFrame()

    with st.spinner('Reading files... Thinking....', show_time=True):
        with st.empty():
            for idx, row in df.iterrows():
                text = get_text(row['Full Path'])
                if text is None:
                    continue
                response = ask(text,
                            st.session_state["question_input"],
                            st.session_state["model_input"])
                if response:
                    try:
                        r_js = json.loads(response)
                        df = pd.DataFrame({k:[v] for k, v in r_js.items()})
                    except Exception as e:
                        print(e)
                        df = pd.DataFrame({'raw':[response]})
                        df['Path'] = row['Full Path']
                    out = pd.concat([out, df]).reset_index(drop=True)
                    st.dataframe(out.tail(5))                           
                else:
                    st.write('Connection error !!! Try 2 minutes later')

            st.write('List saved... -> data.xlsx')
            out.to_excel('data.xlsx')
                