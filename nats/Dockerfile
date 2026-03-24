FROM nats:2.10-alpine

RUN mkdir -p /etc/nats /nats-config

COPY nats-server.conf /nats-config/nats-server.conf
COPY docker-entrypoint.sh /docker-entrypoint.sh
RUN chmod +x /docker-entrypoint.sh

EXPOSE 4222 7422 8222 8443

ENTRYPOINT ["/docker-entrypoint.sh"]
