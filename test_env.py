import os, pathlib, sys
from dotenv import load_dotenv

env_path = pathlib.Path(__file__).resolve().parent / ".env"
print("env_path:", env_path, "| exists:", env_path.exists())

load_dotenv(dotenv_path=env_path, override=True)

if env_path.exists():
    with open(env_path, encoding="utf-8", errors="ignore") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                k = k.strip()
                v = v.strip().strip('"').strip("'")
                if k and v and not os.environ.get(k):
                    os.environ[k] = v

print("NVIDIA_API_KEY:", bool(os.getenv("NVIDIA_API_KEY")))
print("FIREWORKS_API_KEY:", bool(os.getenv("FIREWORKS_API_KEY")))
print("TAVILY_API_KEY:", bool(os.getenv("TAVILY_API_KEY")))
print("GEMINI_API_KEY:", bool(os.getenv("GEMINI_API_KEY")))
print("GOOGLE_API_KEY:", bool(os.getenv("GOOGLE_API_KEY")))
