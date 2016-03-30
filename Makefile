SOURCES=$(shell find . -name '*.py' | grep -v test_)
TESTS=$(shell find . -name 'test_*.py')

check: $(SOURCES)
	@for c_file in $$(echo $(TESTS)); do         \
	  echo "running test suite : $${c_file}";    \
	  PYTHONPATH=. python3 $${c_file} $(ARGS) || true; \
	 done

.cov-buit: $(SOURCES) $(TESTS)
	@rm -f .coverage
	@for c_file in $$(echo $(TESTS)); do \
	  PYTHONPATH=. coverage run --omit 'xtd/test/*' -a --branch $${c_file} || true;  \
	 done
	@touch $@

.cov-report-built: .cov-buit
	@coverage html -d build/coverage
	@touch $@

cov: .cov-buit .cov-report-built

show-cov: .cov-report-built
	@sensible-browser build/coverage/index.html
