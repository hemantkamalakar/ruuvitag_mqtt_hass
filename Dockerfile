FROM arm32v7/python:3.6-slim
WORKDIR /app
COPY . /app
RUN apt-get update && apt-get install -y \
    gcc \
    python-psutil \
    bluez \
    sudo \
    bluez-hcidump
RUN pip install --upgrade pip
COPY requirements.txt ./
RUN pip install -r requirements.txt
CMD ["python", "/app/ruuvi.py", "config.yaml"]
