.PHONY: build run test

build:
	docker build -t ma-chat .

run:
	docker run -it --rm \
		-e PYTHONPATH=/app/src \
		ma-chat

test:
	docker run -it --rm \
		-e PYTHONPATH=/app \
		ma-chat python -m pytest -q