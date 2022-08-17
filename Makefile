SHELL := bash
.SHELLFLAGS := -eu -o pipefail -c
.ONESHELL:
.DELETE_ON_ERROR:
MAKEFLAGS += --warn-undefined-variables
MAKEFLAGS += --no-builtin-rules

.SILENT:

all: stamps/thingo stamps/potato

stamps/thingo: stamps/ohno stamps/shabazz
	echo updating $@ because $?
	echo 'thingo!' >$@

stamps/ohno: stamps/shibuya
	echo "doing something elaborate with an API or whatever (btw $$(date -r $< +%Y-%m-%d))"
	sleep 5
	echo ohno >$@

stamps/potato: stamps/whatever
	echo some other thing taking a bit
	sleep 3
	echo potato >$@

.PHONY: all
