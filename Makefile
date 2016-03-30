SOURCES=$(shell find . -name '*.py' | grep -v test_)
SOURCEDIRS=$(shell find . -name '*.py' | grep -v test | xargs dirname | sort -u)
TESTS=$(shell find . -name 'test_*.py')

check: $(SOURCES)
	@for c_file in $$(echo $(TESTS)); do         \
	  echo "running test suite : $${c_file}";    \
	  PYTHONPATH=. python3 $${c_file} $(ARGS) || true; \
	 done

.cov-buit: $(SOURCES) $(TESTS) Makefile
	@rm -f .coverage
	@for c_file in $$(echo $(TESTS)); do \
	  PYTHONPATH=. coverage3 run --source="$(shell echo $(SOURCEDIRS) | sed 's/ /,/g')" --omit 'xtd/test/*' -a --branch $${c_file} || true;  \
	 done
	@touch $@

.cov-report-built: .cov-buit
	@coverage3 html -d build/coverage
	@touch $@

cov: .cov-buit .cov-report-built

show-cov: .cov-report-built
	@sensible-browser build/coverage/index.html

clean:
	@rm -rf .cov-buit .cov-report-built .coverage build/coverage
