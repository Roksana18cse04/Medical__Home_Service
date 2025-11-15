# MediUrgency Docker Setup

## Build Docker Image

```powershell
docker build -t mediurgency:latest .
```

## Run Docker Container

### Basic run (expose port 8000):

```powershell
docker run -p 8000:8000 mediurgency:latest
```

### Run with environment variables (.env):

```powershell
docker run -p 8000:8000 --env-file .env mediurgency:latest
```

### Run with mounted volume for audio files:

```powershell
docker run -p 8000:8000 -v C:\path\to\temp_audio:/app/temp_audio mediurgency:latest
```

### Run in background (detached mode):

```powershell
docker run -d -p 8000:8000 --name mediurgency-app mediurgency:latest
```

### View logs from running container:

```powershell
docker logs -f mediurgency-app
```

### Stop container:

```powershell
docker stop mediurgency-app
```

### Remove container:

```powershell
docker rm mediurgency-app
```

## Docker Compose (optional, for multi-service setup)

Create a `docker-compose.yml` file if you want to run with MongoDB, Redis, or other services:

```yaml
version: '3.8'

services:
  app:
    build: .
    ports:
      - "8000:8000"
    environment:
      - MONGODB_URL=mongodb://mongo:27017
      - ENVIRONMENT=production
    depends_on:
      - mongo
    volumes:
      - ./temp_audio:/app/temp_audio

  mongo:
    image: mongo:latest
    ports:
      - "27017:27017"
    volumes:
      - mongo_data:/data/db

volumes:
  mongo_data:
```

Run with Docker Compose:

```powershell
docker-compose up -d
```

## Environment Variables

Create a `.env` file in the project root:

```
MONGODB_URL=mongodb://localhost:27017
GEMINI_API_KEY=your-gemini-key
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
ENVIRONMENT=development
```

## Verify Container is Running

Access FastAPI docs at: `http://localhost:8000/docs`

Access ReDoc at: `http://localhost:8000/redoc`

## Build for Production

```powershell
docker build -t mediurgency:prod --target production .
```

(Note: Update Dockerfile with production stage if needed.)
