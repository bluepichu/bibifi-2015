ROOT_DIR = $(abspath $(dir $(lastword $(MAKEFILE_LIST))))

bibifilib = $(shell find bibifi -type f -iname '*.py')

all: bank atm

bank: $(bibifilib) main_bank.py
	sed "s:XXX:$(ROOT_DIR):" < main_$@.py > $@
	chmod +x $@

atm: $(bibifilib) main_atm.py
	sed "s:XXX:$(ROOT_DIR):" < main_$@.py > $@
	chmod +x $@

test:
	python3 -m pytest

clean:
	rm -f *.card *.auth
	rm -f atm bank
	rm -f *.zip
	rm -f __main__.py

.PHONY: all test clean
