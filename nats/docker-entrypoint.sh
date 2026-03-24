#!/bin/sh
set -e

CONF="/etc/nats/nats-server.conf"

# Copy config to writable location
cp /nats-config/nats-server.conf "$CONF"

# Substitute tokens from environment variables
sed -i "s|LEAFNODE_TOKEN_PLACEHOLDER|${NATS_LEAFNODE_TOKEN:-change-me-leafnode}|g" "$CONF"
sed -i "s|INTERNAL_TOKEN_PLACEHOLDER|${NATS_INTERNAL_TOKEN:-change-me-internal}|g" "$CONF"

exec nats-server -c "$CONF"
