#!/bin/bash

python add_news_source.py

if [ ! -f done_initial_crawl ]; then
  python initial_crawl.py
  touch done_initial_crawl
fi

./subscriber.sh &
./storage.sh &
