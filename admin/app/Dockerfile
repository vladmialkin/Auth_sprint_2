FROM python:3.12

WORKDIR /opt/app

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV DJANGO_SETTINGS_MODULE "config.settings"

RUN apt update && apt install gettext -y && pip install --upgrade pip
COPY /requirements/base.txt requirements.txt
RUN pip install -r requirements.txt

COPY /scripts /scripts
RUN chmod +x /scripts/entrypoint.sh

COPY . .

EXPOSE 8000

ENTRYPOINT [ "/scripts/entrypoint.sh" ]
