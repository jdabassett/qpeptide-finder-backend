## Local Development Setup

1. Copy the example environment file:sh
   cp .env.example .env
   2. Update `.env` with your local values (already configured for Docker Compose)

3. Start the services:sh
   docker-compose -f docker-compose.local.yml up --build
   4. The database will be created automatically and migrations will run.
