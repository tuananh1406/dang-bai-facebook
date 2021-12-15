#!/bin/bash
cd /home/htuananh/facebook
echo -n `date '+[%d/%m/%Y %H:%M:%S] --'` && pipenv run python auto_post_fb.py >> log.txt
