#!/usr/bin/env bash

host="$1"
shift
port="$1"
shift
cmd="$@"

echo "Host: $host"
echo "Port: $port"
echo "Command: $cmd"

until nc -z "$host" "$port"; do
  echo "Waiting for $host:$port to be available..."
  sleep 2
done

echo "$host:$port is available, executing command: $cmd"
exec $cmd
