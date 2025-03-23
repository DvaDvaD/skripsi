FROM stablebaselines/rl-baselines3-zoo-cpu

USER root

COPY ./tools/deeprest/ /tool/
COPY ./apis/*/specifications/* /specifications/
COPY ./apis/*/dictionaries/* /dictionaries/

RUN apt update && \
    apt install -y default-jdk && \
    mkfifo /tool/j2p && \
    mkfifo /tool/p2j

CMD cd /tool && \
    sh config.sh && \
    python3 deeprest.py & \
    cd /tool && java -jar resttestgen.jar -l WARN
