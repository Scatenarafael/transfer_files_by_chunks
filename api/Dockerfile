FROM python:3.11.4-slim-bullseye AS BASE
# Set environment variables
ENV PIP_DISABLE_PIP_VERSION_CHECK 1
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

COPY . /app


WORKDIR /app     

#RUN python3 -m venv photondam_env

#RUN chmod +x photondam_env/bin/activate

#RUN photondam_env/bin/activate
RUN pip install pip --upgrade
RUN pip install -r requirements.txt
RUN chmod +x entrypoint.sh

CMD ["./entrypoint.sh"]