#!/usr/bin/env bash

# run this with a cron job

USER=""
JERKBOT_DIR=""

su -c "cd $JERKBOT_DIR; ./jerkbot.py" $USER
