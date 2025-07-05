# Running The Gold Monkey Project with Docker

This guide explains how to build and run the entire Gold Monkey project—including the Streamlit app and all MCP servers—using Docker and Docker Compose.

---

## Prerequisites

- [Docker](https://docs.docker.com/get-docker/) installed (version 20.10+ recommended)
- [Docker Compose](https://docs.docker.com/compose/) (comes with Docker Desktop or install separately)
- (Optional) A `.env` file in the project root for environment variables (see `.env.example`)

---

## 1. Build the Docker Images

From the project root, run:

```bash
docker compose build
```

This will build a single image for all services using your `Dockerfile` and `pyproject.toml`/`uv.lock`.

---

## 2. Start All Services

To start the Streamlit app and all MCP servers:

```bash
docker compose up --build -d
```

- The main app will be available at [http://localhost:8501](http://localhost:8501)
- All MCP servers (SaltyBot, Roku, Spotify, TP-Link, RAG, Voice) will run in the background

To run in detached mode (in the background):
```bash
docker compose up -d
```

---

## 3. Stopping Services

To stop all running containers:
```bash
docker compose down
```

---

## 4. Environment Variables

- The `.env` file is used for all services. Make sure it contains all required API keys and settings.
- **Do not commit secrets to version control!**
- You can override variables at runtime with `--env` or by editing `.env`.

---

## 5. Persistent Data (Optional)

If you want to persist data (e.g., in the `data/` directory), uncomment the `volumes` section in `docker-compose.yml`:

```yaml
  # volumes:
  #   - ./data:/app/data
```

This will map your local `data/` folder to the container, so changes are saved between runs.

---

## 6. Logs & Troubleshooting

- View logs for all services:
  ```bash
  docker compose logs
  ```
- View logs for a specific service:
  ```bash
  docker compose logs saltybot
  ```
- Restart a single service:
  ```bash
  docker compose restart voice
  ```
- If you change dependencies, rebuild with:
  ```bash
  docker compose build
  ```

---

## 7. Advanced

- **Custom Ports:** Edit the `ports` section in `docker-compose.yml` if you want to change the exposed port.
- **Production:** Use Docker secrets or environment variables for sensitive data.
- **Cloud:** This setup works on any Docker-compatible cloud (AWS ECS, Azure, GCP, etc.).

---

## 8. Common Issues

- **Port already in use:** Stop other apps using port 8501 or change the port mapping.
- **Missing .env:** Copy `.env.example` to `.env` and fill in required values.
- **File permissions:** On Linux, you may need to adjust permissions for mounted volumes.

---

## 9. Need Help?

If you have issues, check the logs, review your `.env` file, and ensure all dependencies are installed. For further help, open an issue or ask your friendly AI assistant! 