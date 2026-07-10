.PHONY: verify verify-python demo-chaos demo-space clean

verify: verify-python demo-chaos

verify-python:
	python3 -m compileall -q src tests chaos partie-aerospatiale
	PYTHONPATH=src python3 -m unittest discover -s tests -v
	bash -n chaos/faketime_demo.sh

demo-chaos:
	python3 chaos/controlled_clock_demo.py

demo-space:
	python3 partie-aerospatiale/spice_time_demo.py --download