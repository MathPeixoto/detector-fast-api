run:
	uvicorn app:app --host="0.0.0.0" --port=8081 --reload
install:
	pip install -t lib -r requirements.txt

.PHONY: run install