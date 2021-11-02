FROM jjanzic/docker-python3-opencv:contrib-opencv-4.0.1 as base
WORKDIR /app
COPY requirements.txt /app
RUN pip install --upgrade pip
RUN pip install -r requirements.txt
COPY ./recognition /app/recognition


############### Start New Image: DEBUGGER #############

FROM base as debug
RUN pip install debugpy

#build --target=debug
ENTRYPOINT ["python","-m","debugpy","--listen", "0.0.0.0:5678","--wait-for-client","recognition/main.py"]

############ PRIMARY ################################

FROM base as primary

CMD ["python", "recognition/main.py"]