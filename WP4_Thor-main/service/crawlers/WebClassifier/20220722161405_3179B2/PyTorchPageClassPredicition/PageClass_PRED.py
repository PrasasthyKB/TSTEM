import os
import numpy as np
import torch
import transformers
import bentoml
from bentoml.frameworks.pytorch import PytorchModelArtifact
from bentoml.adapters import FileInput, JsonOutput ,DataframeInput, JsonInput
from bentoml.service.artifacts.common import PickleArtifact
from transformers import LongformerForSequenceClassification, LongformerModel, LongformerConfig, LongformerTokenizer


@bentoml.env(pip_packages=['bentoml==0.13.1', 'torch==1.12.0','protobuf==3.20','pillow==8.1.0','numpy==1.22.4','transformers==4.19.4','torchvision'])
@bentoml.env(pip_extra_index_url=['https://download.pytorch.org/whl/cpu'])
@bentoml.artifacts([PytorchModelArtifact('model'),PickleArtifact('tokenizer')])

class PyTorchPageClassPredicition(bentoml.BentoService):

   
    def predict(self,to_predict):
        
        tokenizer = self.artifacts.tokenizer
        model = self.artifacts.model
        # encode text
        encoded_data = tokenizer(str(to_predict),return_tensors='pt',padding = 'max_length', truncation=True)
        
        preds_batch = model(encoded_data['input_ids'].to('cpu'), attention_mask=encoded_data['attention_mask'].to('cpu')) [0]
        preds = preds_batch.detach().numpy()
        label = np.argmax(preds, axis=-1) [0]
        return label
       
        
    @bentoml.api(input=DataframeInput(), batch=True)
    def page_class_predict(self, to_predict):
            #df = pd.read_json(df_json)
            #to_predict = df.cleaned_domain.apply(lambda x: x.replace('\n', ' ')).tolist()
            label = self.predict(to_predict) 
            return label
