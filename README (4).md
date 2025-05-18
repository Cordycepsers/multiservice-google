# Cloud Run Webhook Authentication

Secure webhook authentication system for Google Cloud Run services.

## Setup

1. Clone the repository:
```bash
git clone https://github.com/cordyceps/multiservice-google.git
cd multiservice-google/auth
```

2. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set environment variables:
```bash
export PROJECT_NUMBER="your-project-number"
export SERVICE_ID="your-service-id"
export REGION="your-region"
export BUCKET_NAME="your-bucket-name"
```

## Development

Run locally:
```bash
python main.py
```

Build and run Docker:
```bash
docker build -t webhook-auth .
docker run -p 8080:8080 webhook-auth
```

## Deploy

Deploy to Cloud Run:
```bash
gcloud builds submit --tag gcr.io/YOUR_PROJECT_ID/webhook-auth
gcloud run deploy webhook-auth \
  --image gcr.io/YOUR_PROJECT_ID/webhook-auth \
  --platform managed \
  --region YOUR_REGION
```