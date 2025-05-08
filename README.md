# TrendStory Project

## Overview
TrendStory is a backend-driven service designed for processing and analyzing trending data using Natural Language Processing (NLP). It utilizes gRPC to provide efficient communication for high-performance applications. The system is intended to handle large-scale, real-time data processing, offering insights into trends by analyzing textual data.

## Features
- `gRPC-based Communication`: High-performance and scalable communication through gRPC for fast request-response cycles.
- `NLP Processing`: Uses NLP models to analyze textual data, helping identify trends and patterns.
- `Backend Focused`: Currently a backend-only service with no frontend component.

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

 ##  Docker Setup (Optional)
For containerized deployment, a Dockerfile is included. To run TrendStory in a Docker container, follow these steps

### 1. Build the Docker Image
```
docker build -t trendstory .
```

### 2. Run the Docker Container
```
docker run -p 50051:50051 trendstory
```

## Architecture
- `grpc_server.py`: Runs a gRPC server for NLP processing.
- `app.py`: Entry point for starting the backend application.
- `agent.proto`: Defines gRPC service contract.
- `finalnlpbackend.py`: Contains NLP logic and integration.
- `Dockerfile`: For containerized deployment.

## Frontend (Streamlit)
TrendStory includes an interactive Streamlit frontend that allows users to explore NLP-based trend analysis visually.

## Features:
Text input and upload support

Real-time trend detection and visualization

Integration with the gRPC backend for live data processing

## Run the Frontend:
Make sure your gRPC server is running first. Then launch the frontend:

bash
Copy
Edit
streamlit run streamlit_app.py
Replace streamlit_app.py with your actual Streamlit script name if different.

