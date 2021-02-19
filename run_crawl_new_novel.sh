#!/bin/bash

if [ $(ps -ef | grep "python manage.py run_crawl_new_novel" | grep -v grep | wc -l) -eq 0 ]; then
	.venv/bin/python manage.py run_crawl_new_novel >/dev/null 2>&1 >>/data/cdn/novel/run_crawl_new_novel.log
fi
