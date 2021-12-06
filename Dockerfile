FROM debian:11
WORKDIR /app

COPY Makefile ./
RUN apt-get update && \
    apt-get install -y make tini && \
    make install-build-dependencies && \
    rm -rf /var/lib/apt/lists/*

COPY . ./

ENV PYTHONUNBUFFERED=1
CMD ["tini", "--", "python3", "-m", "main", "trace"]
