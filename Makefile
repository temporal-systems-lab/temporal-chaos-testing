.PHONY: verify verify-python verify-wheel demo-chaos demo-space clean

DIST_DIR ?= dist
WHEEL_VENV ?= .wheel-venv

verify: verify-python demo-chaos verify-wheel

verify-python:
	python3 -m compileall -q src tests chaos partie-aerospatiale
	PYTHONPATH=src python3 -m unittest discover -s tests -v
	bash -n chaos/faketime_demo.sh

verify-wheel:
	@if python3 -c 'import ensurepip' >/dev/null 2>&1; then \
		rm -rf $(DIST_DIR) $(WHEEL_VENV); \
		python3 -m venv $(WHEEL_VENV); \
		. $(WHEEL_VENV)/bin/activate && pip wheel --no-deps --wheel-dir $(DIST_DIR) . && pip install $(DIST_DIR)/*.whl && temporal-chaos list >/dev/null && temporal-chaos controlled-clock >/dev/null; \
	else \
		echo "ensurepip unavailable; skipping wheel smoke test locally"; \
	fi

demo-chaos:
	python3 chaos/controlled_clock_demo.py

demo-space:
	python3 partie-aerospatiale/spice_time_demo.py --download

clean:
	rm -rf $(DIST_DIR) $(WHEEL_VENV)