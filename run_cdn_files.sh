#!/bin/bash

if [ $(ps -ef | grep "python manage.py run_cdn_files" | grep -v grep | wc -l) -lt 2 ]; then
	.venv/bin/python manage.py run_cdn_files >/dev/null 2>&1 >>/data/cdn/novel/run_cdn_files.log
fi
