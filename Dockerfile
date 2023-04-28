FROM python:3.10-slim-buster

WORKDIR /backend

COPY ./requirements.txt /backend/requirements.txt
RUN apt-get update && apt-get install -y tesseract-ocr
RUN apt-get install libgl1-mesa-glx -y
RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir --upgrade -r /backend/requirements.txt

COPY ./main.py /backend/main.py
COPY ./utils /backend/utils
COPY ./services /backend/services
COPY ./yolo_model /backend/yolo_model
COPY ./table_service_account_keys.json /backend/table_service_account_keys.json

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]