from docx import Document
import pandas as pd
from docx.oxml.text.paragraph import CT_P
from docx.oxml.table import CT_Tbl
from docx.text.paragraph import Paragraph
from docx.table import Table
import json
import re

def df_to_ndjson_str(df):
    records = df.to_dict(orient="records")
    lines = [json.dumps(rec, ensure_ascii=False) for rec in records]
    return "\n".join(lines)

def parse_docx(file_path, nrow=5):
    doc = Document(file_path)
    body = doc.element.body
    blocks = []
    for child in body.iterchildren():
        # Paragraph
        if isinstance(child, CT_P):
            p = Paragraph(child, doc)
            text = p.text.strip()
            if text:
                blocks.append({"type": "paragraph", "text": text})

        # Table
        elif isinstance(child, CT_Tbl):
            t = Table(child, doc)
            table_data = []
            for idx, row in enumerate(t.rows):
                row_data = [cell.text.strip() for cell in row.cells]
                if idx==0:
                    columns = [f'{e}_{i}' for i, e in enumerate(row_data)] 
                else:
                    table_data.append(row_data)

            df = pd.DataFrame(table_data, columns=columns).head(nrow)
            df_ndjson = df_to_ndjson_str(df)
            blocks.append({"type": "table", "text": df_ndjson})

    df = pd.DataFrame(blocks) # Cols = type, text, file_type
    df['file_type'] = 'docx'

    return df


def cleaner(df):
    BIDI_CHARS = ["\u202A", "\u202B", "\u202D", "\u202E", "\u202C", "\u2066", "\u2067", "\u2068", "\u2069", "\u200E", 
                "\u200F", "\u061C"]

    pattern = "[" + "".join(map(re.escape, BIDI_CHARS)) + "]"
    df["text"] = df["text"].str.replace(pattern, "", regex=True)
    df["text"] = df["text"].str.replace("\t"," ", regex=True)
    df = df[df["text"].str.strip().str.len()>0].reset_index(drop=True)

    return df

def get_text(file_path):
    df = parse_docx(file_path)
    df = cleaner(df)
    text = '\n'.join(df['text'])
    return text