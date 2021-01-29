#!/bin/bash

# -e	errexit	Abort script at first error, when a command exits with non-zero status (except in until or while loops, if-tests, list constructs)
# -u	nounset	Attempt to use undefined variable outputs error message, and forces an exit
# x	xtrace	Similar to -v, but expands commands
# -v	verbose	Print each command to stdout before executing it
#set -evx;
set -e

#########################
# The command line help #
#########################
display_help() {
	echo "Usage: $0 [option...] {-i|-mi|-mm|-rg|-rn|-ru|-rm|-f}" >&2
	echo
	echo "   -h | --help    help"
	echo "   -i           	install requirements"
	echo "   -mi          	migrate"
	echo "   -mm           	makemigrations"
	echo "   -rg           	reset git"
	echo "   -rn           	restart nginx"
	echo "   -ru           	restart uwsgi"
	echo "   -rm           	restart memcached"
	echo "   -f           	Full - run all the above commands"
	echo
	# echo some stuff here for the -a or --add-options
	exit 1
}

# Get arguments
args=("$@")

i=1
for item in "$@"; do
	# echo "Item - $i: $item"
	case $item in
	-h | --help)
		display_help
		exit 0
		;;
	-i) install_requirements="$item" ;;
	-mm) make_migrations="$item" ;;
	-mi) migrate="$item" ;;
	-rg) reset_git="$item" ;;
	-rn) restart_nginx="$item" ;;
	-ru) restart_uwsgi="$item" ;;
	-rm) restart_memcached="$item" ;;
	-f) full="$item" ;;
	*)
		echo "$item" "is invalid"
		display_help
		exit 1
		;;
	esac
	i=$((i + 1))
done

# -z Return true if a bash variable is unset or set to the empty string
# -n Return true if a bash variable is set or not empty string

echo "Fetching ... "
git fetch

if [[ -n "$reset_git" || -n "$full" ]]; then
	echo "Reset hard git to HEAD ... "
	git reset --hard
fi

echo "Pulling ... "
git pull

if [[ -n "$install_requirements" || -n "$full" ]]; then
	echo "Installing requirement ... "
	.venv/bin/pip install -r requirements.txt
fi

if [[ -n "$make_migrations" || -n "$full" ]]; then
	echo "Make migrations ... "
	.venv/bin/python manage.py makemigrations
fi

if [[ -n "$migrate" || -n "$full" ]]; then
	echo "Migrating ... "
	.venv/bin/python manage.py migrate
fi

if [[ -n "$restart_nginx" || -n "$full" ]]; then
	echo "Restart Nginx ... "
	sudo systemctl restart nginx.service
fi

if [[ -n "$restart_uwsgi" || -n "$full" ]]; then
	echo "Restart uWSGI ... "
	sudo systemctl restart uwsgi.service
fi

if [[ -n "$restart_memcached" || -n "$full" ]]; then
	echo "Restart Memcache ... "
	sudo systemctl restart memcached.service
fi
