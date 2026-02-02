import os
import json
from datetime import datetime
from typing import List, Dict, Optional
from src.exceptions import StorageError


class FileManager:
    def __init__(self, base_dir: str = "output"):
        self.base_dir = base_dir
        self.manifest_path = os.path.join(base_dir, "manifest.json")
        os.makedirs(base_dir, exist_ok=True)
        if not os.path.exists(self.manifest_path):
            self._save_manifest([])

    def _load_manifest(self) -> List[Dict]:
        try:
            with open(self.manifest_path, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            raise StorageError(f"Failed to load manifest: {e}")

    def _save_manifest(self, manifest: List[Dict]):
        try:
            with open(self.manifest_path, 'w') as f:
                json.dump(manifest, f, indent=2)
        except Exception as e:
            raise StorageError(f"Failed to save manifest: {e}")

    def _get_unique_filename(self, filename: str, year: int, month: int) -> str:
        """Handle filename collisions by prefixing with timestamp if needed."""
        base_path = os.path.join(self.base_dir, str(year), f"{month:02d}")
        full_path = os.path.join(base_path, filename)
        if not os.path.exists(full_path):
            return filename
        # Add timestamp prefix
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        name, ext = os.path.splitext(filename)
        return f"{timestamp}_{name}{ext}"

    def save_pdf(self, pdf_bytes: bytes, filename: str, metadata: Dict) -> str:
        """
        Save PDF to organized directory and update manifest.
        metadata should include at least 'invoice_number', and optionally others.
        Returns the full path of the saved file.
        """
        now = datetime.now()
        year = now.year
        month = now.month
        unique_filename = self._get_unique_filename(filename, year, month)
        dir_path = os.path.join(self.base_dir, str(year), f"{month:02d}")
        os.makedirs(dir_path, exist_ok=True)
        full_path = os.path.join(dir_path, unique_filename)

        with open(full_path, 'wb') as f:
            f.write(pdf_bytes)

        # Update manifest
        manifest = self._load_manifest()
        entry = {
            'filename': unique_filename,
            'path': full_path,
            'generated_at': now.isoformat(),
            'year': year,
            'month': month,
            **metadata
        }
        manifest.append(entry)
        self._save_manifest(manifest)

        return full_path

    def list_reports(self, year: Optional[int] = None, month: Optional[int] = None, invoice_number: Optional[str] = None) -> List[Dict]:
        """List reports with optional filtering."""
        manifest = self._load_manifest()
        filtered = manifest
        if year is not None:
            filtered = [r for r in filtered if r.get('year') == year]
        if month is not None:
            filtered = [r for r in filtered if r.get('month') == month]
        if invoice_number is not None:
            filtered = [r for r in filtered if r.get('invoice_number') == invoice_number]
        return filtered

    def get_report_path(self, filename: str) -> Optional[str]:
        """Get the full path of a report by filename."""
        manifest = self._load_manifest()
        for entry in manifest:
            if entry['filename'] == filename:
                return entry['path']
        return None

    def get_report_content(self, filename: str) -> Optional[bytes]:
        """Retrieve the PDF content by filename."""
        path = self.get_report_path(filename)
        if path and os.path.exists(path):
            with open(path, 'rb') as f:
                return f.read()
        return None

    def delete_report(self, filename: str) -> bool:
        """Delete a report and update manifest."""
        manifest = self._load_manifest()
        for i, entry in enumerate(manifest):
            if entry['filename'] == filename:
                path = entry['path']
                if os.path.exists(path):
                    os.remove(path)
                manifest.pop(i)
                self._save_manifest(manifest)
                return True
        return False