#!/bin/bash

# see https://docs.google.com/spreadsheets/d/1pAtz8v2gnkkrAdNrhhrpICkTNQ8cd1ObduUsphcbqp4/edit#gid=0
# for a mapping between physical pin and
# "Chip" and "Linux #"
SWITCH_PIN=91
CHIP=1

gpioset "$CHIP" "$SWITCH_PIN"="$1"
