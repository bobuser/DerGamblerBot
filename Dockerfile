FROM python:buster

WORKDIR /usr/src/app
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
RUN apt-get update && apt-get install wkhtmltopdf -y
COPY . ./

CMD [ "python", "gamblebot.py" ]