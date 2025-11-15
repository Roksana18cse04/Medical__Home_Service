# UV Package Manager Setup & Usage

`uv` is a fast Python package installer written in Rust. It's much faster than pip for installing dependencies.

## Install UV (local machine)

```powershell
pip install uv
```

Or if you use conda:

```powershell
conda install uv
```

## Using UV to Install Requirements

### Option 1: Install to system Python

```powershell
uv pip install -r requirements.txt
```

### Option 2: Install to virtual environment

```powershell
# Create venv
python -m venv .venv

# Activate venv
.\.venv\Scripts\Activate

# Install using uv
uv pip install -r requirements.txt
```

### Option 3: Install specific packages

```powershell
uv pip install fastapi uvicorn
```

## Running FastAPI with UV

After installing dependencies with `uv`, run normally:

```powershell
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## Performance Comparison

| Tool | Time (approx) | Speed |
|------|---------------|-------|
| pip | 3-5 min | Standard |
| uv   | 30-60 sec | **10x faster** |

## Docker Build with UV

The Dockerfile already includes `uv` installation and uses:

```dockerfile
RUN uv pip install --system -r requirements.txt
```

Build and run:

```powershell
docker build -t mediurgency:latest .
docker run -p 8000:8000 mediurgency:latest
```

## UV Sync (lock file generation - optional)

Generate a lock file for reproducible installs:

```powershell
uv pip compile requirements.txt -o requirements.lock
```

Then install from lock file:

```powershell
uv pip install -r requirements.lock
```

## Notes

- `uv pip install` is a drop-in replacement for `pip install` (same syntax).
- UV is now the standard in modern Python projects (used by projects like Ruff, Astral).
- The Docker Dockerfile uses `uv` by default for faster builds.
- If you prefer pip, replace `uv pip install` with `pip install` in Dockerfile.

## Troubleshooting

If you get errors with UV, fall back to pip:

```powershell
pip install -r requirements.txt
```

Or update Dockerfile to use pip instead:

```dockerfile
RUN pip install --no-cache-dir -r requirements.txt
```
