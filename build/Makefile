
bibifilib = $(shell find bibifi -type f -iname '*.py')

all: bank atm

bank: $(bibifilib) main_bank.py
	cp main_$@.py __main__.py
	zip -0 $@.zip __main__.py $(bibifilib)
	echo '#!/usr/bin/env python3' | cat - $@.zip > $@
	chmod +x $@
	rm -f __main__.py $@.zip

atm: $(bibifilib) main_atm.py
	cp main_$@.py __main__.py
	zip -0 $@.zip __main__.py $(bibifilib)
	echo '#!/usr/bin/env python3' | cat - $@.zip > $@
	chmod +x $@
	rm -f __main__.py $@.zip

test:
	python3 -m pytest

clean:
	rm -f *.card *.auth
	rm -f atm bank
	rm -f *.zip
	rm -f __main__.py

.PHONY: all test clean
