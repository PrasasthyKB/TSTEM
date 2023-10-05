import json
from iocextract import extract_iocs, extract_hashes, extract_emails, extract_urls
import torch
import pandas as pd
import nltk
nltk.download('punkt')
from msticpy.sectools import IoCExtract
import PyTorchnerPredicition
from nltk import tokenize
import re
import datetime
import time

def json_reader(file_name: str):
    with open(file_name, 'r') as f:
        try:
            return json.loads(f.read())
        except Exception as e:
            return e
        

def extract_indicator_of_compromise(data):
  payload = {}
  iocs = []
  mapping = [ ('[.', '.'), ('.]', '.'),('[.]', '.'), ('(.)', '.'), ('{.}', '.'), ('hxxp', 'http'), ('\.', '.'), ('[@]', '@'), ('(@)', '@'), ('{@}', '@'), ('[/]', "//"), ('hxpp', 'http') ]
  text = str(data['data']['text'])
  print("text:", text)
  print("type:", type(text))
  for k, v in mapping:
      text = text.replace(k, v)
  print("final text:", text)
  ner_instance = PyTorchnerPredicition.load()
  payload['text'] = data['data']['text']
  payload['@timestamp'] = datetime.datetime.now().replace(microsecond=0).isoformat()
  #iocs['created_at'] = datetime.datetime.strptime(data['created_at'], "%a %b %d %H:%M:%S %z %Y")  
  payload['id'] = data['data']['id']
  payload["iocs"] = []
  st = time.time()
  IOC_list = ner_instance.ner_predict(text)
  print("IOC_list:", IOC_list)
  ioc_extractor = IoCExtract()
  # Adding btc regex
  ioc_extractor.add_ioc_type(ioc_type='btc', ioc_regex='^(?:[13]{1}[a-km-zA-HJ-NP-Z1-9]{26,33}|bc1[a-z0-9]{39,59})$')
  
  ioctable = pd.DataFrame([])
  #sentences_list = tokenize.sent_tokenize(data['text'])
  #for i in range(0, len(sentences_list)): 
  #iocs_found = ioc_extractor.extract(sentences_list[i])
  iocs_found = ioc_extractor.extract(text)
  print('iocs_found:', iocs_found)
  for k, v in iocs_found.items():
     for i in iocs_found[k].copy():
          ioc = {}
          ioc[k] = i
          data = pd.DataFrame(ioc.items())
          ioctable = ioctable.append(data)

  df = ioctable
  df =df.rename(columns = {0:'IOC_type', 1: 'IOC'})
  df.reset_index(inplace=True)
  print('df:', df)
  final_IOC_df = pd.DataFrame()
  #ioc_exists = True
  if len(df) != 0:
     IOC_type = [df['IOC_type'].unique]
     if len(IOC_type) != 0:
         for i in range(0, len(df)):
             if df.loc[i, 'IOC'] in IOC_list:
                 print(df.loc[i, 'IOC'])
                 final_IOC_df.loc[i, 'IOC_type'] = df.loc[i, 'IOC_type']
                 final_IOC_df.loc[i, 'IOC'] = df.loc[i, 'IOC']
         final_IOC_df.reset_index( inplace=True)
     if len(final_IOC_df) != 0:
         for j in range(0,len(final_IOC_df )):
            iocs.append({"type":final_IOC_df.loc[j, 'IOC_type'], "value":final_IOC_df.loc[j, 'IOC'] })
       #v1IOC_type = list(final_IOC_df['IOC_type'].unique())
       #v1IOC_final_list = list(final_IOC_df['IOC'].unique())
       #v1if len(IOC_type) != 0:    
         #v1for i in range(0, (len(IOC_type))):
             #print(IOC_type[i]) v2
             #iocs[IOC_type[i]] = list(set(final_IOC_df.loc[final_IOC_df['IOC_type'] == IOC_type[i], 'IOC']))v2
          #v1   iocs.append({"type":IOC_type[i], "value": list(set(final_IOC_df.loc[final_IOC_df['IOC_type'] == IOC_type[i], 'IOC']))})

         #iocs['others'] = list(set(IOC_list) - set(IOC_final_list))v2
  #elif len(IOC_list) !=0:v2
  #     iocs['others'] = list(set(IOC_list))v2
            ioc_exists = True
     else:
          for i in range(0, len(df)):
                 IOC_type_value   = df.loc[i, 'IOC_type']
                 #iocs[IOC_type_value] = df.loc[i, 'IOC']
                 iocs.append({"type":IOC_type_value, "value": df.loc[i, 'IOC']})
                 ioc_exists = True
  else:
       ioc_exists = False
  et = time.time()
  payload["classification_time"] = et - st
  payload["iocs"] = iocs
  return ioc_exists, payload