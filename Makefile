SHELL := bash
.SHELLFLAGS := -eu -o pipefail -c
.ONESHELL:
MAKEFLAGS += --warn-undefined-variables
MAKEFLAGS += --no-builtin-rules
MAKEFLAGS += --keep-going

.SILENT:

all: stamps/thingo stamps/potato

clean:
	-rm stamps/*

stamps/failure:
	echo add me to 'all' if you want to see --keep-going in action
	exit 1

stamps/thingo: stamps/ohno stamps/shabazz
	echo updating $@ because $?
	echo 'thingo!' >$@

stamps/ohno: stamps/shibuya
	{
		flock -x 3
		echo "doing something elaborate with an API or whatever (btw upstream updated at $$(date -r $< +%Y-%m-%d))"
		sleep 30
		echo $(*F) >$@
	} 3>/tmp/$(*F).lock

stamps/potato: stamps/whatever
	{
		flock -x 3
		echo some other thing taking a bit
		sleep 3
		echo $(*F) >$@
	} 3>/tmp/$(*F).lock

.PHONY: all clean
