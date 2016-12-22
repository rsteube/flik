#!/bin/sh
tag=${1:-latest}
clear
docker run -i -t --rm \
           -v "flik-console:/root/.config/flik" \
           -v "flik-console:/root/.local/share/flik" \
           rsteube/flik:${tag}
