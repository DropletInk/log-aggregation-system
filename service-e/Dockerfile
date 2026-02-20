FROM gcc:12

WORKDIR /app

COPY main.c .

RUN gcc main.c -o service-e

CMD ["./service-e"]
