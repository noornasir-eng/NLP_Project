FROM pytorch/pytorch:2.0.0-cuda11.7-cudnn8-runtime

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install base dependencies first with compatible versions
# Use grpcio 1.71.0 to match the generated code requirement
RUN pip install --no-cache-dir grpcio==1.71.0 grpcio-tools==1.71.0 protobuf>=4.21.6

# Install compatible versions of huggingface_hub and accelerate
RUN pip install --no-cache-dir huggingface_hub>=0.19.0 accelerate==0.26.1

# Copy only proto file first to generate compatible gRPC files
COPY agent.proto .
RUN python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. agent.proto

# Now install the rest of the requirements
COPY requirements-minimal.txt .
RUN pip install --no-cache-dir -r requirements-minimal.txt

# Install compatible transformers and bitsandbytes
RUN pip install --no-cache-dir transformers==4.35.2 --timeout 300
RUN pip install --no-cache-dir bitsandbytes==0.37.0 --timeout 300

# PyTorch is already included in the base image, so no need to install it again

# Copy the rest of the application code
COPY . .

# Set environment variables
ENV USE_LIGHTWEIGHT_MODEL=true
ENV FORCE_CPU=true

# Expose the gRPC port
EXPOSE 50051

# Command to run the gRPC server
CMD ["python", "grpc_server.py"]
