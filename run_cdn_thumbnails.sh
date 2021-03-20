#!/bin/bash

if [ $(ps -ef | grep "python manage.py run_cdn_thumbnails" | grep -v grep | wc -l) -lt 2 ]; then
	.venv/bin/python manage.py run_cdn_thumbnails >/dev/null 2>&1 >>/data/cdn/novel/run_cdn_thumbnails.log
fi
