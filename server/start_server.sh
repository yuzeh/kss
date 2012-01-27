#!/bin/sh
sudo node /usr/local/bin/forever start \
     -l /home/dan/log/kss-forever.log \
     -o /home/dan/log/kss-out.log \
     -e /home/dan/log/kss-err.log \
     server.js
