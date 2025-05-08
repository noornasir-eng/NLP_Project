# TrendStory Project

## Overview
TrendStory is a backend-driven NLP-based service designed to process and analyze trending data using gRPC for efficient communication.

## Setup Instructions

### Requirements
- Python 3.10+
- pip
- Docker (optional for containerized deployment)

### Installation
1. Create a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Run the gRPC server:
   ```
   python grpc_server.py
   ```

4. Run the main app:
   ```
   python app.py
   ```

## Architecture
- `grpc_server.py`: Runs a gRPC server for NLP processing.
- `app.py`: Entry point for starting the backend application.
- `agent.proto`: Defines gRPC service contract.
- `finalnlpbackend.py`: Contains NLP logic and integration.
- `Dockerfile`: For containerized deployment.

## Model Sources
The system uses NLP models and libraries specified in `finalnlpbackend.py`.

## Limitations
- Currently no frontend.
- Only supports basic gRPC request-response structure.
- No user authentication or role management.

