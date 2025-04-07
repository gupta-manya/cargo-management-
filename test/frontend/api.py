# frontend/api.py
import requests

BASE_URL = "http://127.0.0.1:8000"

def upload_csv_to_backend(file, endpoint: str):
    files = {"file": (file.name, file.getvalue(), "text/csv")}
    response = requests.post(f"{BASE_URL}/{endpoint}", files=files)
    return response
