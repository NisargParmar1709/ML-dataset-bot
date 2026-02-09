import os
import shutil
import zipfile
import requests
import logging
from typing import List, Optional
from config import Config

logger = logging.getLogger(__name__)

class FileManager:
    """
    Handles file downloading, zipping, splitting, and cleanup.
    """

    @staticmethod
    def download_file(url: str, dest_filename: str) -> Optional[str]:
        """
        Downloads a file from a URL to the TEMP_DIR.
        """
        try:
            local_path = os.path.join(Config.TEMP_DIR, dest_filename)
            logger.info(f"⬇️ Starting download: {url} -> {local_path}")
            
            with requests.get(url, stream=True) as r:
                r.raise_for_status()
                total_length = int(r.headers.get('content-length', 0))
                downloaded = 0
                
                with open(local_path, 'wb') as f:
                    for chunk in r.iter_content(chunk_size=8192):
                        f.write(chunk)
                        downloaded += len(chunk)
                        # Log progress every 5MB roughly
                        if total_length > 0 and downloaded % (5 * 1024 * 1024) < 10000:
                            percent = int((downloaded / total_length) * 100)
                            logger.info(f"⏳ Downloading {dest_filename}: {percent}% ({downloaded//(1024*1024)}MB / {total_length//(1024*1024)}MB)")
            
            logger.info(f"✅ Download complete: {local_path} ({os.path.getsize(local_path)//(1024*1024)}MB)")
            return local_path
        except Exception as e:
            logger.error(f"❌ Failed to download file from {url}: {e}")
            return None

    @staticmethod
    def zip_directory(dir_path: str, output_name: str) -> Optional[str]:
        """
        Zips a directory into a single file.
        """
        try:
            zip_path = os.path.join(Config.TEMP_DIR, f"{output_name}.zip")
            logger.info(f"🗜️ Zipping directory {dir_path} -> {zip_path}...")
            
            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for root, dirs, files in os.walk(dir_path):
                    for file in files:
                        file_path = os.path.join(root, file)
                        arcname = os.path.relpath(file_path, dir_path)
                        zipf.write(file_path, arcname)
            
            size_mb = os.path.getsize(zip_path) // (1024 * 1024)
            logger.info(f"✅ Zipping complete: {zip_path} ({size_mb}MB)")
            return zip_path
        except Exception as e:
            logger.error(f"❌ Failed to zip directory {dir_path}: {e}")
            return None

    @staticmethod
    def split_large_file(file_path: str, limit_bytes: int = Config.CHUNK_SIZE) -> List[str]:
        """
        Splits a file into chunks if it exceeds the limit.
        Returns a list of chunk paths.
        """
        file_size = os.path.getsize(file_path)
        if file_size <= limit_bytes:
            return [file_path]
        
        chunk_paths = []
        try:
            logger.info(f"✂️ Splitting large file: {file_path} ({file_size//(1024*1024)}MB) into {limit_bytes//(1024*1024)}MB chunks")
            with open(file_path, 'rb') as f:
                chunk_idx = 0
                while True:
                    chunk = f.read(limit_bytes)
                    if not chunk:
                        break
                    
                    chunk_name = f"{file_path}.part{chunk_idx+1}"
                    with open(chunk_name, 'wb') as chunk_file:
                        chunk_file.write(chunk)
                    chunk_paths.append(chunk_name)
                    chunk_idx += 1
                    logger.info(f"   Created chunk {chunk_idx}: {chunk_name}")
            
            return chunk_paths
        except Exception as e:
            logger.error(f"❌ Failed to split file {file_path}: {e}")
            return []

    @staticmethod
    def cleanup(paths: List[str]):
        """
        Removes files or directories.
        """
        for path in paths:
            try:
                if os.path.isdir(path):
                    shutil.rmtree(path)
                elif os.path.isfile(path):
                    os.remove(path)
                logger.debug(f"🧹 Cleaned up: {path}")
            except Exception as e:
                logger.warning(f"⚠️ Failed to cleanup {path}: {e}")
