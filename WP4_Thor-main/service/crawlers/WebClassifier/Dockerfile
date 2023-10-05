# As Scrapy runs on Python, I choose the official Python 3 Docker image.
FROM python:3.8.10

# Set the working directory to /usr/src/app.
WORKDIR /usr/src/classifier

# Copy the file from the local host to the filesystem of the container at the working directory.
COPY requirements.txt ./

# Install dependecies specified in requirements.txt.
RUN pip3 install --no-cache-dir -r requirements.txt

ADD "20220722161405_3179B2" ./20220722161405_3179B2
RUN pip install "./20220722161405_3179B2"
ADD "20221017201834_3D1751" ./20221017201834_3D1751
RUN pip install "./20221017201834_3D1751"

# Copy the project source code from the local host to the filesystem of the container at the working directory.
COPY IoCClassifier.py .
COPY utils.py .
#COPY config.json .
#COPY ./model_checkpoints ./model_checkpoints

ENV PYTHONUNBUFFERED=1
CMD [ "python", "-u", "IoCClassifier.py"]
