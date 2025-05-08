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

## Model Sources
The application relies on NLP models and libraries to perform trend analysis and data processing. These models are integrated and specified in the finalnlpbackend.py module. Currently, these models are focused on basic text analysis and are ready for extensions to include more complex models and additional NLP tasks.

## Limitations
- `Frontend`: There is currently no frontend available. The service is backend-only, and users interact with it through gRPC.
- `Basic Request`: Response Structure: The communication between the client and server follows a basic request-response pattern using gRPC. More advanced features like streaming or bidirectional communication are not yet supported.
- `No User Authentication or Role Management`: There is no built-in user authentication or role-based access management in the system. This can be added as an enhancement for future releases.


