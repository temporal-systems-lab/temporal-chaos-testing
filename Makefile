.PHONY: verify verify-python verify-wheel verify-space-offline verify-space-online demo-chaos demo-space clean

DIST_DIR ?= dist
WHEEL_VENV ?= .wheel-venv
RUNTIME_PYTHONPATH := $(if $(PYTHONPATH),$(PYTHONPATH):)src

verify: verify-python demo-chaos verify-wheel

verify-python:
	python3 -m compileall -q src tests chaos partie-aerospatiale
	PYTHONPATH=src python3 -m unittest discover -s tests -v
	bash -n chaos/faketime_demo.sh

verify-wheel:
	@if python3 -c 'import ensurepip' >/dev/null 2>&1; then \
		rm -rf $(DIST_DIR) $(WHEEL_VENV); \
		python3 -m venv $(WHEEL_VENV); \
		. $(WHEEL_VENV)/bin/activate && pip wheel --no-deps --wheel-dir $(DIST_DIR) . && pip install $(DIST_DIR)/*.whl && temporal-chaos list >/dev/null && temporal-chaos controlled-clock >/dev/null && temporal-chaos holdover >/dev/null && temporal-chaos leap-smear-mismatch >/dev/null && temporal-chaos certificate-expiry >/dev/null && temporal-chaos lease-pause >/dev/null && temporal-chaos jwt-totp-skew >/dev/null && temporal-chaos ptp-grandmaster-failover >/dev/null; \
	else \
		echo "ensurepip unavailable; skipping wheel smoke test locally"; \
	fi

demo-chaos:
	PYTHONPATH=src python3 -m temporal_chaos_testing.cli list
	PYTHONPATH=src python3 -m temporal_chaos_testing.cli controlled-clock
	PYTHONPATH=src python3 -m temporal_chaos_testing.cli holdover
	PYTHONPATH=src python3 -m temporal_chaos_testing.cli leap-smear-mismatch
	PYTHONPATH=src python3 -m temporal_chaos_testing.cli certificate-expiry
	PYTHONPATH=src python3 -m temporal_chaos_testing.cli lease-pause
	PYTHONPATH=src python3 -m temporal_chaos_testing.cli jwt-totp-skew
	PYTHONPATH=src python3 -m temporal_chaos_testing.cli ptp-grandmaster-failover

demo-space:
	python3 partie-aerospatiale/spice_time_demo.py --download

verify-space-offline:
	PYTHONPATH=$(RUNTIME_PYTHONPATH) python3 -m unittest discover -s tests -p 'test_spice_demo.py' -v
	@if python3 -c 'import spiceypy' >/dev/null 2>&1; then \
		PYTHONPATH=$(RUNTIME_PYTHONPATH) python3 -m temporal_chaos_testing.scenarios.spice_time_demo; \
	else \
		echo "spiceypy not installed; skipping offline SPICE execution locally"; \
	fi

verify-space-online:
	@if python3 -c 'import spiceypy' >/dev/null 2>&1; then \
		rm -rf build/spice-online-kernels; \
		PYTHONPATH=$(RUNTIME_PYTHONPATH) python3 -m temporal_chaos_testing.scenarios.spice_time_demo --download --kernel-dir build/spice-online-kernels; \
	else \
		echo "spiceypy not installed; skipping online SPICE execution locally"; \
	fi

clean:
	rm -rf $(DIST_DIR) $(WHEEL_VENV)