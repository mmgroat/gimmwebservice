FROM python:3.13-slim-bookworm
WORKDIR /app
COPY ./requirements.txt /app
RUN pip install -r requirements.txt
RUN pip install filelock
RUN pip install ordered_set
RUN pip install setuptools
COPY . .
COPY classes/ classes/
COPY static/ static/
EXPOSE 5010
ENV FLASK_APP=gimmwebservice.py
ENV FLASK_DEBUG=1
ENV FLASK_RUN_PORT=5010
CMD ["flask", "run", "--host=0.0.0.0"]
