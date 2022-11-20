#!/bin/bash

# see https://docs.google.com/spreadsheets/d/1pAtz8v2gnkkrAdNrhhrpICkTNQ8cd1ObduUsphcbqp4/edit#gid=0
# for a mapping between physical pin and
# "Chip" and "Linux #"
switch_pin=91
chip=1


if command -v gpioset
then
    gpioset "$chip" "$switch_pin"="$1"
else
    echo "gpioset does not exist; aborting" >&2
    exit 1
fi
