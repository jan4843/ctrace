APT_INSTALL ?= apt-get install --assume-yes --no-install-recommends

docker-run:
	docker compose up --build

install-runtime-dependencies:
	$(APT_INSTALL) \
		linux-headers-$(shell uname -r)

install-build-dependencies:
	$(APT_INSTALL) \
		python3-bpfcc \
		python3-docker \
		python3-seccomp

test:
	python -m unittest discover -s tests
