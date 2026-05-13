FROM python:3.12-slim

WORKDIR /app
COPY ion_kernel/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

COPY ion_kernel /app/ion_kernel
COPY capability_graph /app/capability_graph
CMD ["uvicorn", "ion_kernel.api:app", "--host", "0.0.0.0", "--port", "8080"]
