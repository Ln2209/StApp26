.PHONY: install data run test
install:
	pip install -r requirements.txt
data:            # optional: download raw CSVs (needs URLs in data/sources.json), then rebuild processed tables
	python -m utils.io
	python -m utils.io --build
run:
	streamlit run app.py
test:
	python -c "from streamlit.testing.v1 import AppTest; at=AppTest.from_file('app.py',default_timeout=180).run(); assert not at.exception, at.exception; print('OK')"
