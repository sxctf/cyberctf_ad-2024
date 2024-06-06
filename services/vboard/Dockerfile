FROM python:3.10

RUN mkdir -p /app
WORKDIR /app

COPY requirements.txt /app
RUN pip install --no-cache-dir -r requirements.txt

#EXPOSE 7000

#ENTRYPOINT ["./start.sh"]
