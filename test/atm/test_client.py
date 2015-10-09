from bibifi.atm.cient import *
import sys

def test_client():
	valid_tests = [
		"-a acc -n 10.00",
		"-a acc -d 10.00",
		"-a acc -w 10.00",
		"-a acc -g",
		"-aacc -n10.00",
		"-s bank.auth -i 127.0.0.1 -p 3000 -c acc.card -a acc -n 10.00"
	]

	invalid_tests = [
		("-a acc -n 9.99", 255),
		("-a acc -d 0.00", 255),
		("-a acc -w 0.00", 255)
	]

	for test in valid_tests:
		sys.argv = test.split(" ")
		# do someting with the method here;
		#   not sure at what point it needs
		#   to stop; and how to simply test
		#   not crashing?

	for test, exit in invalid_tests:
		sys.argv = test.split(" ")
		with SystemExit as exit:
			# call method here
		# assert proper exit code here