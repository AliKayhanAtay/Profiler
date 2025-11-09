import streamlit as st
import time
import pandas as pd
import os
import uuid
import time
from pathlib import Path
from extractor import get_text
from ollama import generate
import requests
from prompt import *
import json

model = 'qwen3:8b'
question = 'Is there any personal information in the document ?'
def ask(text, question, model=model):
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
                st.write(f'File locations are being scanned... {c} files scanned')
                c += 1
                time.sleep(.1)

    df = pd.DataFrame(rows)
    out = pd.DataFrame()
    tt = 0
    with st.spinner('Reading files...', show_time=True):
        with st.empty():
            for idx, row in df.iterrows():
                text = get_text(row['Full Path'])
                response = ask(text,
                            st.session_state["question_input"],
                            st.session_state["model_input"])
                try:
                    r_js = json.loads(response['message']['content'])
                    df = pd.DataFrame({k:[v] for k, v in r_js.items()})
                except:
                    df = pd.DataFrame({'raw':[response['message']['content']]})
                    df['Path'] = row['Full Path']

                out = pd.concat([out, df]).reset_index(drop=True)
                out.index += 1 
                tt += response['total_duration'] / 1e-9
                ta = tt / (idx+1)
                minutes, seconds = divmod(int(ta), 60)
                ta = f"{minutes:02d}:{seconds:02d}"

                st.dataframe(out.tail(5))   
        df.to_excel('data.xlsx')
                
            





# if st.session_state["folder_path"] is not None:
#     directory = Path(text_input)
#     rows = []    
#     file_paths = []
#     c = 0
#     with st.empty():
#         for current_root, dirs, files in os.walk(text_input):
#             for name in files:
#                 full_path = os.path.join(current_root, name)
#                 file_paths.append(full_path)
#                 st.write(f'File locations are being scanned... {c} files scanned')
#                 c += 1
#                 time.sleep(.1)

# with title_row:
#     if st.button("Reset"):
#         st.session_state.clear()   # drop all session keys
#         st.rerun()     

# if "uploader" not in st.session_state:
#     st.session_state.uploader_key = 0


# with st.sidebar:
#     input_file = st.file_uploader('Raporunuzu Yükleyiniz...', type=['docx'], accept_multiple_files=False, key='uploader', 
#                                   help=None, on_change=None, args=None, kwargs=None, disabled=False, 
#                               label_visibility="visible", width="stretch")
    

# if st.session_state["uploader"] is not None:
#     with st.spinner("Rapor okunuyor...", show_time=True):
#         df = GetDocxText(input_file.getvalue()) 
#         df_table = df[df['type']=='table']['text']
#         upload_id = uuid.uuid4().hex
    
#     with open(f"files/{upload_id}_{input_file.name}.docx", "wb") as f:
#         f.write(input_file.getvalue())
#     #PushFile(upload_id, f'{upload_id}_{input_file.name}.docx', str(USER), Now())        

#     with st.container(border=True):
#         st.header('Tablo Toplamları kontrol ediliyor...', anchor=None,  help=None, divider=False, width="stretch")
#         # Stream the LLM response.
#         with st.spinner("Thinking...", show_time=True):
#             st.write(f'{len(df_table)} tablo bulundu. Kontrol ediliyor...')
#             for i, table in enumerate(df_table, start=1):
#                 response = ''.join([e for e in Ask(prompt_system=ps_check_sum, prompt_user=pu_check_sum.format(table))])
#                 response_clean = Trim_think(response)
#                 st.write(f'Tablo - {i}')
#                 st.write_stream(TextGen(response_clean))

#     with st.container(border=True):
#         with st.container(border=True):
#             st.header('Yazım Hataları', anchor=None,  help=None, divider=False, width="stretch")
#             # Stream the LLM response.
#             html_list = GetHtml(df)
#             st.html(html_list)
                
# #     with st.container(border=True):
# #                 st.header('Tutarlılık', anchor=None,  help=None, divider=False, width="stretch")
# #                 # Stream the LLM response.
# #                 with st.spinner("Thinking...", show_time=True):
# #                     response = st.write_stream(Ask(prompt_check_semantic.format(input_file_text)))        

#     with st.container(border=True):
#         temp1 = df_sim[(df_sim['OTHER_TYPE']=='bulgu')&(df_sim['KEY']==input_file.name)]
#         temp1 = temp1.nlargest(5, 'score')

#         st.header('Bulgular', anchor=None,  help=None, divider=False, width="stretch")
#         cols=['KEY', 'TEXT', 'score', 'OTHER_KEY', 'OTHER_Resolution', 'OTHER_URL', 'OTHER_TEXT']
#         st.dataframe(temp1[cols], hide_index=True, row_height=100,
#                      column_config={"OTHER_URL": st.column_config.LinkColumn(
#                                     "Website",display_text="Open",     # fixed link text (optional)
#                                     max_chars=None)           # don’t truncate
#                                     },)              

#     with st.container(border=True):
#         temp1 = df_sim[(df_sim['OTHER_TYPE']=='rehber')&(df_sim['KEY']==input_file.name)]
#         temp1 = temp1.nlargest(5, 'score')

#         st.header('Rehberler', anchor=None,  help=None, divider=False, width="stretch")
#         cols=['KEY', 'TEXT', 'score', 'OTHER_KEY',  'OTHER_URL', 'OTHER_TEXT']
#         st.dataframe(temp1[cols], hide_index=True, row_height=100,
#                      column_config={"OTHER_URL": st.column_config.LinkColumn(
#                                     "Website",display_text="Open",     # fixed link text (optional)
#                                     max_chars=None)           # don’t truncate
#                                     },)              
