DPM ?= $(if $(wildcard $(HOME)/.dpm/bin/dpm),$(HOME)/.dpm/bin/dpm,dpm)
REPO_ROOT := $(abspath $(dir $(lastword $(MAKEFILE_LIST))))
export XDG_CACHE_HOME := $(REPO_ROOT)/target/cache
export TMPDIR := $(REPO_ROOT)/target/tmp

.PHONY: build test
build:
	@mkdir -p "$(XDG_CACHE_HOME)" "$(TMPDIR)"
	cd contracts && "$(DPM)" build --all

test: build
	cd contracts/test && "$(DPM)" test --show-coverage --junit "$(REPO_ROOT)/target/contracts-junit.xml"
