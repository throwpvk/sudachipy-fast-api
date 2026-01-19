# SudachiPy API

FastAPI service for Japanese text tokenization and normalization using SudachiPy.

## Features

- Japanese text tokenization
- Text normalization
- Part-of-speech tagging
- Batch processing support
- Docker support for easy deployment

## Local Development

### Prerequisites

- Python 3.11+
- pip

### Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Run the server
python main.py
```

The API will be available at `http://localhost:8000`

## Docker Deployment

### Build and run with Docker

```bash
# Build the image
docker build -t sudachipy-api .

# Run the container
docker run -p 8000:8000 sudachipy-api
```

### Using Docker Compose

```bash
# Start the service
docker-compose up -d

# Stop the service
docker-compose down
```

## Deploy to Render

1. Create a new Web Service on Render
2. Connect your GitHub repository
3. Set the following:
   - **Environment**: Docker
   - **Docker Build Context Path**: `./sudachipy-api` (if in subdirectory)
   - **Port**: 8000
4. Deploy

### Environment Variables (Optional)

No environment variables required for basic setup.

## API Endpoints

### Health Check

```bash
GET /health
```

Response:

```json
{
  "status": "healthy",
  "service": "sudachipy-api",
  "version": "1.0.0"
}
```

### Tokenize Single Text

```bash
POST /tokenize
Content-Type: application/json

{
  "text": "日本語を学ぶ。"
}
```

Response:

```json
{
  "success": true,
  "raw": "日本語を学ぶ。",
  "normalized": "日本語を学ぶ。",
  "normalized_spaced": "日本語 を 学ぶ 。",
  "tokens": [
    {
      "surface": "日本語",
      "base": "日本語",
      "pos": "名詞",
      "reading": "ニホンゴ"
    },
    {
      "surface": "を",
      "base": "を",
      "pos": "助詞",
      "reading": "ヲ"
    },
    {
      "surface": "学ぶ",
      "base": "学ぶ",
      "pos": "動詞",
      "reading": "マナブ"
    },
    {
      "surface": "。",
      "base": "。",
      "pos": "補助記号",
      "reading": null
    }
  ]
}
```

### Process Multiple Sentences (Main Endpoint)

```bash
POST /process
Content-Type: application/json

{
  "sentences": [
    {
      "id": 1,
      "raw": "日本語を学ぶ。"
    },
    {
      "id": 2,
      "raw": "すごいですね。"
    }
  ]
}
```

Response:

```json
{
  "success": true,
  "sentences": [
    {
      "id": 1,
      "raw": "日本語を学ぶ。",
      "normalized": "日本語を学ぶ。",
      "normalized_spaced": "日本語 を 学ぶ 。",
      "tokens": [...]
    },
    {
      "id": 2,
      "raw": "すごいですね。",
      "normalized": "すごいですね。",
      "normalized_spaced": "すごい です ね 。",
      "tokens": [...]
    }
  ]
}
```

## Testing

```bash
# Test health endpoint
curl http://localhost:8000/health

# Test tokenize endpoint
curl -X POST http://localhost:8000/tokenize \
  -H "Content-Type: application/json" \
  -d '{"text": "日本語を学ぶ。"}'

# Test process endpoint
curl -X POST http://localhost:8000/process \
  -H "Content-Type: application/json" \
  -d '{"sentences": [{"id": 1, "raw": "日本語を学ぶ。"}]}'
```

## Integration with NestJS

The NestJS backend should call the `/process` endpoint with an array of sentences to get normalized text and tokens for all sentences in batch.

See the NestJS furigana service for integration details.
