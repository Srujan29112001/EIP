# EIP backend — Hugging Face Space (Docker SDK) / any container host
FROM python:3.12-slim

WORKDIR /app

# non-root user (required by HF Spaces)
RUN useradd -m -u 1000 user

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
RUN mkdir -p /app/data && chown -R user:user /app

USER user
EXPOSE 7860

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "7860"]
