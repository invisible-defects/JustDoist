FROM python:3.6-alpine

ENV PYTHONBUFFERED 1

RUN mkdir /justdoist
WORKDIR justdoist
ADD . /justdoist/

RUN set -ex \
    && apk add --no-cache --virtual .build-deps \
            gcc \
            make \
            libc-dev \
            musl-dev \
            linux-headers \
            pcre-dev \
            postgresql-dev \
            python3-dev \
            libxslt-dev \
            libffi-dev \
    && LIBRARY_PATH=/lib:/usr/lib /bin/sh -c "pip install --no-cache-dir -r requirements.txt" \
    && PDEPS=$(python -c "import sys, os; print(os.path.dirname(os.path.dirname(sys.executable)))") \
    && runDeps="$( \
            scanelf --needed --nobanner --recursive $PDEPS \
                    | awk '{ gsub(/,/, "\nso:", $2); print "so:" $2 }' \
                    | sort -u \
                    | xargs -r apk info --installed \
                    | sort -u \
    )" \
    && apk add --virtual .python-rundeps $runDeps \
    && apk del .build-deps

EXPOSE 8000
