FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

RUN useradd -m myuser
USER myuser

COPY app/ .

EXPOSE 5000

ENV FLASK_APP=__init__.py
ENV FLASK_ENV=development

CMD ["python", "-m", "flask", "run", "--host=0.0.0.0"]
