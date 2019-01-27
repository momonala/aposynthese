#!/usr/bin/env bash

# Install dependencies, source code
sudo apt-get update
sudo apt-get install -y ffmpeg nodejs npm python3-pip git
git clone https://github.com/momonala/aposynthese.git
cd aposynthese
sudo npm install
pip3 install -r requirements.txt

# Run the app
sudo npm start
