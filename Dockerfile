FROM python:alpine
WORKDIR /usr/src/app

RUN apk update && apk add postgresql-dev gcc python3-dev musl-dev libffi-dev openssl-dev
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
#RUN   apk del libressl-dev musl-dev libffi-dev
COPY . .

CMD [ "python", "./gamblebot.py" ]
