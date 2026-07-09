import os
import zipfile
from typing import List
from utils.config import DOWNLOAD_DIR, OUTPUT_DIR

def save_file(file_id: str, file_bytes: bytes, filename: str) -> str:
    ext = os.path.splitext(filename)[1]
    local_path = os.path.join(DOWNLOAD_DIR, f"{file_id}{ext}")
    with open(local_path, "wb") as f:
        f.write(file_bytes)
    return local_path

def create_zip_archive(file_paths: List[str], archive_name: str) -> str:
    zip_path = os.path.join(OUTPUT_DIR, archive_name)
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for file in file_paths:
            if os.path.exists(file):
                zipf.write(file, os.path.basename(file))
    return zip_path

def clean_files(file_paths: List[str]) -> None:
    for path in file_paths:
        try:
            if os.path.exists(path):
                os.remove(path)
        except Exception:
            pass
