#!/bin/bash

while true; do
  #statements

  for i in {1..2}
  do
    python download_content.py &
  done

  python download_content.py

  echo "sleep 300"
  sleep 300

done
