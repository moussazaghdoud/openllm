FROM alpine:3.19

# Install NATS server
RUN apk add --no-cache curl && \
    curl -fsSL https://github.com/nats-io/nats-server/releases/download/v2.10.24/nats-server-v2.10.24-linux-amd64.tar.gz | tar xz && \
    mv nats-server-v2.10.24-linux-amd64/nats-server /usr/local/bin/ && \
    rm -rf nats-server-v2.10.24-linux-amd64 && \
    apk del curl

RUN mkdir -p /etc/nats /nats-config

COPY nats-server.conf /nats-config/nats-server.conf
COPY docker-entrypoint.sh /docker-entrypoint.sh
RUN chmod +x /docker-entrypoint.sh

EXPOSE 4222 7422 8222 8443

ENTRYPOINT ["/docker-entrypoint.sh"]
