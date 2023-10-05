import openai
import os
import json
from elasticsearch import Elasticsearch

class GptService:
    def __init__(self, messages):
        openai.organization = os.environ["OPENAI_ORGANIZATION_ID"]
        openai.api_key = os.environ["OPENAI_API_KEY"]
        
        self.contextual_messages = messages
        
    def get_class(self, input):
        response = openai.Completion.create(
        model="babbage:ft-ubicomp:thor-classification-v2-2023-07-19-20-42-05",
        prompt=f"{input}\n\n###\n\n",
        temperature=0,
        max_tokens=1,
        top_p=0.5,
        frequency_penalty=0,
        presence_penalty=0
        )
        response_json = json.dumps(response, indent=2)
        print(response_json)
        input_class = response.choices[0].text.strip()
        print(input_class)
        return input_class

    def send_query_command(self, input):
        response = openai.Completion.create(
            model="babbage:ft-ubicomp:thor-hunt-pro-2023-07-06-15-03-51",
            prompt=f"{input}\n\n###\n\n",
            temperature=0,
            max_tokens=171,
            top_p=0,
            frequency_penalty=0,
            presence_penalty=0,
            stop=[" }"]
        )
        response_json = json.dumps(response, indent=2)
        print(response_json)
        answer_srt = response.choices[0].text.strip() + ' }'
        answer_srt = answer_srt.replace("'", "\"")
        print(answer_srt)
        answer = json.loads(answer_srt)
        
        self.insert_to_elasticsearch(input, answer_srt)
        
        return answer

    def insert_to_elasticsearch(self, input, gpt_response):
        print("*** Inserting to Elasticsearch ***")
        document = {
            'user_input': input,
            'agent_reponse': gpt_response
        }
        
        es = Elasticsearch(
            os.environ['ELASTICSEARCH_SERVER'],
            basic_auth = ('elastic', os.environ['ELASTICSEARCH_PASSWORD'])
        )
        
        response = es.index(index='thor_hunt_pro_chats', body=document)
        
        if response['result'] == 'created':
            print('Document inserted successfully.')
        else:
            print('Failed to insert document.')
            
    def answer_general_questions(self, user_input):
        self.contextual_messages.append({"role": "user", "content" : user_input})
        completion = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages = self.contextual_messages
        )
        print("**** response from openai completion ****")
        print(completion)
        response = completion.choices[0].message.content
        self.contextual_messages.append({"role": "assistant", "content" : response})
        return response
