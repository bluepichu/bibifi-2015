
bibifilib = $(shell find bibifi -type f -iname '*.py')

all: bank atm

bank: $(bibifilib) main_bank.py
	pyinstaller main_bank.py --onefile
	mv dist/main_bank bank

atm: $(bibifilib) main_atm.py
	pyinstaller main_atm.py --onefile
	mv dist/main_atm atm

test:
	python3 -m pytest

clean:
	rm -f *.card *.auth
	rm -f atm bank
	rm -f *.zip
	rm -f __main__.py
	rm -rf dist

.PHONY: all test clean
