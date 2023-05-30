FROM python:3.11.3-bullseye

ARG BUILD_DEPS=" \
	bluez \
    libglib2.0-dev"

RUN apt-get update \
 && apt-get install -y --no-install-recommends \
        ${BUILD_DEPS}

RUN apt-get autoremove -yqq --purge \
 && apt-get clean \
 && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

RUN pip install --upgrade pip
RUN pip install bluepy
RUN pip install git+https://github.com/pybluez/pybluez.git#egg=pybluez

COPY __init__.py /app/
COPY dongleless.py /app/
COPY myo_dicts.py /app/
COPY quaternion.py /app/
COPY vector.py /app/

WORKDIR /app
RUN chmod +x dongleless.py

ENTRYPOINT ["/app/dongleless.py"]
