import os
import torch
import numpy as np
import torch.nn as nn
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
import bentoml
from bentoml.frameworks.pytorch import PytorchModelArtifact
from bentoml.adapters import DataframeInput
from bentoml.service.artifacts.common import PickleArtifact
from transformers import AutoModel, BertTokenizerFast
import re
from iocextract import extract_iocs

@bentoml.env(pip_packages=['bentoml==0.11.0', 'transformers==4.17.0', 'pillow==8.1.0','scikit-learn==0.22', 'iocextract==1.13.1', 'regex==2022.3.15'])
@bentoml.env(pip_extra_index_url=['https://download.pytorch.org/whl/cpu'])
@bentoml.artifacts([PytorchModelArtifact('model'),PickleArtifact('tokenizer')])

class Tweet_classification(bentoml.BentoService):

   
    def predict(self,to_predict):
        
        tokenizer = self.artifacts.tokenizer
        model = self.artifacts.model
        # encode text
        sent_id = tokenizer.batch_encode_plus(to_predict, padding=True, return_token_type_ids=False)
        
        test_seq = torch.tensor(sent_id['input_ids'])
        test_mask = torch.tensor(sent_id['attention_mask'])
        
        # get predictions for data
        with torch.no_grad():
                preds = model(test_seq.to('cpu'), test_mask.to('cpu'))
                preds = preds.detach().cpu().numpy()
        model_output = preds
        preds = np.argmax(preds, axis=1)
        return preds, model_output
    
    def clean_tweet(self, tweet): 
        temp = tweet.lower()
        temp = temp.replace('\n', ' ')
        temp = re.sub("@[A-Za-z0-9_]+","", temp)
        temp = re.sub("#","", temp)
        for ioc in extract_iocs(temp):
            temp = temp.replace(ioc, '')
        temp = re.sub("[^a-z0-9]"," ", temp)
        temp = temp.split()
        temp = " ".join(word for word in temp)
        if len(temp) == 0:
            return ''
        return temp
       
        
    @bentoml.api(input=DataframeInput(), batch=True)
    def classify_tweet(self, df):
            df = self.clean_tweet(df)
            preds, model_outputs = self.predict([df]) 
            return preds[0]
