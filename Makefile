.PHONY: install test app serve benchmark screenshots report ppt diagrams all

install:
	python -m pip install -e .

test:
	python -m pytest -q

app:
	python -m scripts.run_all_applications

serve:
	python -m clawflow.gateway.cli serve

benchmark:
	python -m scripts.run_benchmark

screenshots:
	python -m scripts.generate_screenshots

diagrams:
	python -m scripts.generate_diagrams

report:
	python -m scripts.generate_report

ppt:
	python -m scripts.generate_ppt

all: app benchmark diagrams screenshots report ppt test

