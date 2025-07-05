# Docker Usage

## Build the Docker image
```bash
docker build -t the-gold-monkey .
```

## Run the Docker container
```bash
docker run --env-file .env -p 8501:8501 the-gold-monkey
```

- The app will be available at http://localhost:8501
- The container uses `uv` and `pyproject.toml` for dependency management.
- The `.env` file is used for environment variables. **Do not commit secrets to version control.**

--- 