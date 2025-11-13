# gen_secret.py
import secrets
from pathlib import Path

# Generate a URL-safe 32-byte secret (about 43 chars) — strong enough for JWT HMAC
secret = secrets.token_urlsafe(32)   # or token_hex(32) for hex

env_path = Path(".env")
if env_path.exists():
    print(".env already exists — appending SECRET_KEY (make sure not to overwrite other vars).")

# Append SECRET_KEY to .env (or create if missing)
with open(env_path, "a", encoding="utf-8") as f:
    f.write(f"\nSECRET_KEY={secret}\n")
print("SECRET_KEY generated and appended to .env:")
