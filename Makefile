SHELL := bash
.SHELLFLAGS := -eu -o pipefail -c
.ONESHELL:
.DELETE_ON_ERROR:
MAKEFLAGS += --warn-undefined-variables
MAKEFLAGS += --no-builtin-rules

all: stamps/thingo

stamps/thingo: stamps/shibuya stamps/shabazz
	echo updating $@ because $?
	echo 'thingo!' >$@

.PHONY: all
