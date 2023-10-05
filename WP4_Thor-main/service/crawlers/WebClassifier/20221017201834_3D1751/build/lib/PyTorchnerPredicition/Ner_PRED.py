import os
import numpy as np
import torch
import transformers
import bentoml
from bentoml.frameworks.pytorch import PytorchModelArtifact
from bentoml.adapters import FileInput, JsonOutput ,DataframeInput, JsonInput
from bentoml.service.artifacts.common import PickleArtifact
from transformers import BertTokenizerFast, BertConfig, BertForTokenClassification
from nltk import tokenize


@bentoml.env(pip_packages=['bentoml==0.13.1', 'torch==1.12.0','protobuf==3.20','pillow==8.1.0','numpy==1.22.4','transformers==4.19.4','torchvision'])
@bentoml.env(pip_extra_index_url=['https://download.pytorch.org/whl/cpu'])
@bentoml.artifacts([PytorchModelArtifact('model'),PickleArtifact('tokenizer')])

class PyTorchnerPredicition(bentoml.BentoService):

   
    def predict(self,sentences_list):
        
        tokenizer = self.artifacts.tokenizer
        model = self.artifacts.model
        device = 'cpu'
        MAX_LEN = 128
        IOC_list = []
        ids_to_labels = {0: "B-Malware", 1: "O", 2: "B-Indicator", 3: "I-Indicator", 4: "B-System", 5: "I-System", 6: "B-Organization", 7: "I-Malware", 8: "I-Organization", 9: "B-Vulnerability", 10: "I-Vulnerability"}
        for i in range(0, len(sentences_list)):
        #print("sentences_list:", sentences_list[i].split())
            inputs = tokenizer(sentences_list[i].split(),
                               is_split_into_words=True,
                                return_offsets_mapping=True, 
                                padding='max_length', 
                                truncation=True, 
                                max_length=MAX_LEN,
                                return_tensors="pt") 
            # move to gpu
            ids = inputs["input_ids"].to(device)
            mask = inputs["attention_mask"].to(device)
            # forward pass
            outputs = model(ids, attention_mask=mask)
            logits = outputs[0]

            active_logits = logits.view(-1, model.num_labels) # shape (batch_size * seq_len, num_labels)
            flattened_predictions = torch.argmax(active_logits, axis=1) # shape (batch_size*seq_len,) - predictions at the token level

            tokens = tokenizer.convert_ids_to_tokens(ids.squeeze().tolist())
            token_predictions = [ids_to_labels[i] for i in flattened_predictions.cpu().numpy()]
            wp_preds = list(zip(tokens, token_predictions)) # list of tuples. Each tuple = (wordpiece, prediction)

            prediction = []

            for token_pred, mapping in zip(wp_preds, inputs["offset_mapping"].squeeze().tolist()):
              #only predictions on first word pieces are important
                if mapping[0] == 0 and mapping[1] != 0:
                    prediction.append(token_pred[1])
                else:
                    continue
            #print(sentences_list.split())
            #print("prediction:", prediction)
            word_list = sentences_list[i].split()

            for i in range(0, len(prediction)):
                if prediction[i] == 'B-Indicator' or prediction[i] == 'I-Indicator':
                    print('word_list:', word_list[i])
                    IOC_list.append(word_list[i])

        return IOC_list
       
        
    @bentoml.api(input=DataframeInput(), batch=True)
    def ner_predict(self, to_predict):
            #df = pd.read_json(df_json)
            #label = []
            sentences_list = tokenize.sent_tokenize(to_predict)
            #to_predict = df.cleaned_domain.apply(lambda x: x.replace('\n', ' ')).tolist()
            label = self.predict(sentences_list) 
            return label
