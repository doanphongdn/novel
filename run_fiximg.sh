#!/bin/bash

if [ $(ps -ef | grep "python manage.py run_fiximg" | grep -v grep | wc -l) -eq 0 ]; then
	.venv/bin/python manage.py run_fiximg >/dev/null 2>&1
fi
