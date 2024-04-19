FROM alpine:3
LABEL maintainer="tumf <y.takahara@gmail.com>"

RUN apk add --no-cache coreutils bash python3 py3-pip mongodb-tools curl
RUN python3 -m venv /venv \
  && . /venv/bin/activate \
  && pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib google-cloud-storage google-auth

RUN curl -sSL https://sdk.cloud.google.com | bash
ENV PATH $PATH:/root/google-cloud-sdk/bin

COPY backup.py /backup.py
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]

