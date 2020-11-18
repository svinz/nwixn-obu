FROM  python:3.9-alpine3.12 AS base
WORKDIR /usr/src/app
COPY ./src/requirements.txt ./

RUN pip install -U --no-cache-dir pip setuptools wheel && \
    pip install --no-cache-dir Cython && \ 
    pip install --no-cache-dir -r requirements.txt 
#eRUN apk add gpsd gpsd-clients
FROM base AS prod
COPY ./src ./
#CMD [ "python","server.py" ]

FROM base as debug
RUN pip install ptvsd
COPY ./src ./
CMD ["python", "-m", "ptvsd", "--host" , "0.0.0.0" , "--port", "5678", "--wait", "client.py" , "-config", "configfile.yml" ]

