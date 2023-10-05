FROM python:3.8

WORKDIR /code

COPY requirements.txt requirements.txt

RUN pip install -r requirements.txt
#RUN pip install git+https://github.com/microsoft/msticpy
ADD "20220523165127_E8A2B3" /code/20220523165127_E8A2B3
RUN pip install "./20220523165127_E8A2B3"
ADD "20221017201834_3D1751" /code/20221017201834_3D1751
RUN pip install "./20221017201834_3D1751"
COPY . .

CMD ["python", "-u", "app.py"]