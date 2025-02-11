FROM python:3.11.9-bookworm

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /egorovamin

RUN apt-get update && apt-get install -y netcat-openbsd

COPY poetry.lock pyproject.toml /egorovamin/

RUN pip install --upgrade pip "poetry==1.8.2"

RUN poetry config virtualenvs.create false --local

RUN poetry install --no-dev

COPY . /egorovamin

COPY config/wait-for-it.sh /egorovamin/config/wait-for-it.sh

RUN chmod +x /egorovamin/config/wait-for-it.sh

RUN pip list

CMD ["python", "manage.py"]