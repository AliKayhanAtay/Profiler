import os
import requests
import json
#from ollama import generate

sp = """
You are an expert large language model specialized in DOCUMENT PROFILING and QUESTION ANSWERING.
Output ONLY a valid JSON object. Do not include any other text, explanation, markdown, or formatting. 
Do not apologize. Do not add prefixes or suffixes. 
The output must start with '{' and end with '}' and be parseable by Python's json.loads().

You will always receive:
1) A document text to analyze
2) A question about that document

YOUR TASK
1. Carefully read and briefly PROFILE the document.
2. Answer the given question STRICTLY based on the document content.
3. Produce your output ONLY as a SINGLE VALID JSON OBJECT (no extra text, no explanations, no Markdown, no ```).

Rules:
- Do NOT use outside knowledge; rely only on the given document text.
- If the answer cannot be determined from the document, say so clearly (e.g. "Unclear from document") and explain why in the JSON fields.
- If the document is long, focus on understanding the overall picture and key points.
- For questions like "Does this document contain personal information?":
  - Personal data examples: real person names, email addresses, phone numbers, postal addresses, ID numbers (e.g. national IDs), bank account details (IBAN etc.), license plates, usernames, signatures, biometric data, etc.

OUTPUT FORMAT
You MUST ALWAYS output exactly ONE JSON object with this structure:
{
"type": "string", // Type of the the text(Report, mail)
"language": "string", // Language of the text
"answer": "Yes|No", // The answer
"reason": "string" // Reason 
}

STRICT REQUIREMENTS:
- Output MUST be valid JSON.
- Do NOT change any key names.
- Do NOT add extra top-level keys.
- Do NOT include comments, Markdown, or any text outside the JSON object.
"""

up = """
Below is a document text and a question about that document.
Please follow the instructions in the system prompt: first profile the document, then answer the question.
Return ONLY a single valid JSON object as described in the system prompt.

[DOCUMENT START]
{}
[DOCUMENT END]

[QUESTION]
{}
"""

def ask(text, question, model):
    headers = {"Authorization": f"Bearer {os.getenv('OPENROUTER_KEY')}",
               "Content-Type": "application/json",}

    data = {"model": model,
            "messages": [{"role": "system", "content": sp},
                         {"role": "user", "content": up.format(text, question)}],}

    r = requests.post(os.getenv("OPENROUTER_URL"),
                    headers=headers, data=json.dumps(data))
    if r.status_code==200:
            resp = json.loads(r.text.strip())["choices"][0]["message"]["content"]
            return resp
    else:
          print(r.text)
          return None
    

# def ask_ollama_old(text, question, model):
#     resp = requests.post(
#         "http://localhost:11434/api/chat",
#         json={
#             "model": model,
#             "messages":[{'role': 'system', 'content': sp, }, 
#                         {'role': 'user', 'content': up.format(text, question),}],
#             "stream": False,
#             'format':"json",
#             "options": {"temperature": 0.0,
#                         "top_p": 0.9,
#                         #"num_predict": 256,   # max tokens to generate
#                         #"stop": ["</end>"],   # optional stop tokens
#                         },},)    

#     r = json.loads(resp.text)
#     return r    