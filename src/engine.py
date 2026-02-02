from jinja2 import Environment, FileSystemLoader, TemplateError
from datetime import datetime
import os
import base64
from pathlib import Path
from weasyprint import HTML, CSS
from src.exceptions import TemplateError as DocGenTemplateError, PDFGenerationError


class AssetResolver:
    def __init__(self, base_dir: str = "src"):
        self.base_dir = Path(base_dir)

    def get_asset_uri(self, relative_path: str, embed: bool = False) -> str:
        """
        Get URI for asset. If embed=True, return base64 data URI.
        Otherwise, return file URI. Raises error if file doesn't exist.
        """
        full_path = self.base_dir / relative_path
        if not full_path.exists():
            raise FileNotFoundError(f"Asset file not found: {full_path}")

        if embed:
            # Read file and encode to base64
            with open(full_path, 'rb') as f:
                data = f.read()
            mime_type = self._get_mime_type(full_path.suffix)
            encoded = base64.b64encode(data).decode('ascii')
            return f"data:{mime_type};base64,{encoded}"
        else:
            # Return file URI
            return full_path.as_uri()

    def _get_mime_type(self, extension: str) -> str:
        mime_types = {
            '.png': 'image/png',
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.gif': 'image/gif',
            '.svg': 'image/svg+xml'
        }
        return mime_types.get(extension.lower(), 'application/octet-stream')


class TemplateRenderer:
    def __init__(self, template_dir: str = "src/templates"):
        self.template_dir = template_dir
        self.env = Environment(loader=FileSystemLoader(template_dir))
        # Optionally, add filters or globals
        self.env.globals['now'] = datetime.now
        self.asset_resolver = AssetResolver()

    def render_html(self, template_name: str, invoice, **kwargs):
        """
        Renders the specified template with the invoice data.
        Automatically injects generation timestamp and logo URL.
        """
        try:
            template = self.env.get_template(template_name)
            # For demo, use a hardcoded base64 logo since placeholder file is not a real image
            logo_url = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAUAAAAFCAYAAACNbyblAAAAHElEQVQI12P4//8/w38GIAXDIBKE0DHxgljNBAAO9TXL0Y4OHwAAAABJRU5ErkJggg=="
            context = {
                'invoice': invoice,
                'generated_at': datetime.now().isoformat(),
                'logo_url': logo_url,
                **kwargs
            }
            return template.render(context)
        except TemplateError as e:
            raise DocGenTemplateError(f"Template rendering error in '{template_name}': {str(e)}")
        except Exception as e:
            raise DocGenTemplateError(f"Unexpected error during template rendering: {str(e)}")


class PDFGenerator:
    def __init__(self, template_renderer=None):
        self.renderer = template_renderer or TemplateRenderer()

    def generate_pdf(self, template_name: str, invoice, page_size='a4', margins='10mm', orientation='portrait', title='', author='', **kwargs):
        """
        Generates PDF from template and invoice data.
        Options: page_size ('a4', 'letter', 'legal'), margins (e.g., '10mm'), orientation ('portrait', 'landscape'),
        title and author for metadata.
        """
        try:
            html = self.renderer.render_html(template_name, invoice, **kwargs)
            # Generate CSS for custom page settings
            css_string = f"@page {{ size: {page_size} {orientation}; margin: {margins}; }}"
            css = CSS(string=css_string)
            # Generate PDF
            pdf_bytes = HTML(string=html).write_pdf(stylesheets=[css], title=title, author=author)
            return pdf_bytes
        except Exception as e:
            raise PDFGenerationError(f"PDF generation error: {str(e)}")