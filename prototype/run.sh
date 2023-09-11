#!/bin/bash

if [ "$#" -ne 1 ]; then
    echo "Usage: ./run.sh <URL>"
    exit 1
fi

URL=$1
mkdir -p temp

# Crawl 
echo "[INF] Visiting $URL"
node run-puppeteer.js "$URL" > "./temp/bytecode.dump" 2> /dev/null


if [ $? -ne 0 ]; then
    echo "[ERR] Crawl"
    exit 2
fi

echo "[INF] Finished crawl"

echo "[INF] Run extractor"

python extract-bytecode.py --pup-links ./temp/puppeteer_links.log --bytecode-dump ./temp/bytecode.dump --output ./temp/output-bytecode.log --mapping ./artifacts/vocab/word_mapping.json 

if [ $? -ne 0 ]; then
    echo "[ERR] Bytecode extraction."
    exit 3
fi

echo "[INF] Finished extraction"

python3 classify.py

if [ $? -ne 0 ]; then
    echo "[ERR] Classification."
    exit 4
fi



