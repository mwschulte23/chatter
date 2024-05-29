import streamlit as st
import os
import json
import instructor

from groq import Groq
from dotenv import load_dotenv
load_dotenv()

from models.query_process import Decomposition, GenerateQuery, Inspection


def call_llm(client, response_model, system_msg, user_msg, max_retries=1):
    return client.chat.completions.create(
        model='mixtral-8x7b-32768',
        max_retries=max_retries,
        response_model=response_model,
        messages=[
            {'role': 'system', 'content': system_msg},
            {'role': 'user', 'content': user_msg},
        ]
    )

def process_user_request(client, system_msg, user_query):
    decomposition: Decomposition = call_llm(client, Decomposition, system_msg, user_query)
    query: GenerateQuery = call_llm(client, GenerateQuery, system_msg, decomposition.generate_next_prompt())

    try:
        result = query.execute_query()
        st.table(result.head())

        st.code(query.query)
    except:
        st.markdown('Error occurred plz try again')


if __name__ == '__main__':
    with open('system_msg.txt', 'r') as msg:
        system_msg = msg.read()

    client = Groq(api_key=os.environ.get('GROQ_API_KEY'))
    client = instructor.patch(client, mode=instructor.Mode.TOOLS)

    user_query = st.text_input('Ask Milo', 'What items have a current price below base?')
    process_user_request(client, system_msg, user_query)

    
