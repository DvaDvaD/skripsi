FROM mcr.microsoft.com/dotnet/sdk:6.0-alpine as builder

RUN apk add --no-cache python3 py3-pip

COPY ./tools/restler/src ./src
COPY ./tools/restler/restler ./restler
COPY ./tools/restler/build-restler.py .

RUN python3 build-restler.py --dest_dir /build

RUN python3 -m compileall -b /build/engine

FROM mcr.microsoft.com/dotnet/aspnet:6.0-alpine as target

RUN apk add --no-cache python3 py3-pip
RUN pip3 install --break-system-packages requests applicationinsights

COPY --from=builder /build /RESTler
COPY ./tools/restler/start.sh .
COPY ./apis/*/specifications/* /specifications/

CMD sh start.sh