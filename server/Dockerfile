FROM mcr.microsoft.com/playwright/python:v1.44.0-jammy

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN playwright install --with-deps
COPY . .

EXPOSE 8050

CMD ["sh", "-c", "python3 build_vectorstore.py && python3 server.py"]