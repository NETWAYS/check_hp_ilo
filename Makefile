.PHONY: lint test coverage

lint:
	python -m pylint check_hp_ilo.py
test:
	python -m unittest -v test_check_hp_ilo.py
coverage:
	python -m coverage run -m unittest test_check_hp_ilo.py
	python -m coverage report -m --include check_hp_ilo.py
