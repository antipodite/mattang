#! /bin/sh

# Build and name the imaage if it doesn't exist
if [[ "$(docker image inspect mattang:latest > /dev/null 2>&1 && echo yes || echo no)" == "no" ]]; then
    docker build --tag mattang:latest .
fi

# We need the absolute path to the file to mount to the container it as a volume or bindmount 
get_abs_filename() {
  # $1 : relative filename
  echo "$(cd "$(dirname "$1")" && pwd)/$(basename "$1")"
}

fname=$(get_abs_filename ${@: -1}) # Last arg
echo $fname

# Invoke the python argparse entry point with the args passed to this script
docker run --rm \
       --mount type=bind,source=$fname,target=/langdata,readonly \
       mattang:latest \
       python3 ./mattang/run.py \
       "$@"
