.PHONY: all test clean

all:
	mv atm __main__.py
	zip -r atm.zip __main__.py bibifi
	echo '#!/usr/bin/env python3.4' | cat - atm.zip > atm
	chmod +x atm

	mv bank __main__.py
	zip -r bank.zip __main__.py bibifi
	echo '#!/usr/bin/env python3.4' | cat - bank.zip > bank
	chmod +x bank

	rm __main__.py
	rm atm.zip
	rm bank.zip

clean:
	rm -f *.card *.auth

test:
	python3 -m pytest

