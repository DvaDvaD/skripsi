FROM ubuntu:22.04

RUN mkdir /tool && \
    apt update && \
    apt -y upgrade && \
    apt -y install python3 python3-pip

COPY ./tools/arat-rl/ /tool/
COPY ./apis/*/specifications/* /specifications/

RUN pip3 install -r /tool/requirements.txt

CMD python3 /tool/arat-rl.py /specifications/$API.yaml http://localhost:$PORT 3700