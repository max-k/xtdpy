SOURCES=$(shell find . -name '*.py' | grep -v test_)
TESTS=$(shell find . -name 'test_*.py')

check: $(SOURCES)
	@for c_file in $$(echo $(TESTS)); do \
	  PYTHONPATH=. python3 $${c_file};   \
	 done

cov:
	@rm -f .coverage
	@for c_file in $$(echo $(TESTS)); do \
	  PYTHONPATH=. coverage run --branch $${c_file};   \
	 done
	@coverage html -d build/coverage
	@sensible-browser build/coverage/index.html
