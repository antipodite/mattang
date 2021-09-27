#! /bin/sh

if [[ "$(docker image inspect mattang:latest > /dev/null 2>&1 && echo yes || echo no)" == "no" ]]; then
    docker build --tag mattang:latest .
fi


docker run --rm \
       mattang:latest \
       python3 ./mattang/run.py \
       "$@"
