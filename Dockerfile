FROM python:3.12-slim
WORKDIR /app
COPY orion.py .
ENV ORION_DB=/data/orion.db
CMD ["python","-u","orion.py"]
