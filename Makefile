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

stamps/thingo: stamps/ohno stamps/shabazz stamps/cronme
	echo updating $@ because $?
	echo 'thingo!' >$@

stamps/ohno: stamps/shibuya
	{
		flock -x 3
		echo "doing something elaborate with an API or whatever (btw upstream updated at $$(date -r $< +%Y-%m-%d))"
		sleep 30
		echo $(*F) >$@
	} 3>/tmp/$(*F).lock

# stamps/whatever is an example for an "external only" task: it only
#   gets touched by the TCP server
stamps/potato: stamps/whatever
	{
		SINCE=0001-01-01
		if [[ -e $@ ]]; then
			SINCE=$$(date -r $@ +%Y-%m-%d)
		fi
		flock -x 3
		echo "some other thing taking a bit (self-update last $$SINCE)"
		sleep 3
		echo $(*F) >$@
	} 3>/tmp/$(*F).lock

# example for a task with no dependencies, probably fired by a cron job
# as e.g. FORCE_REMAKE=stamps/cronme make
# (see below)
stamps/cronme:
	{
		SINCE=0001-01-01
		if [[ -e $@ ]]; then
			SINCE=$$(date -r $@ +%Y-%m-%d)
		fi
		flock -x 3
		echo "fetch all records since $$SINCE"
		sleep 5
		echo $(*F) >$@
	} 3>/tmp/$(*F).lock

.FORCE:
$(FORCE_REMAKE): .FORCE

.PHONY: all clean .FORCE
