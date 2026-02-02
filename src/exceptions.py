class DocGenError(Exception):
    """Base exception for DocGen errors."""
    pass


class TemplateError(DocGenError):
    """Raised when template rendering fails."""
    pass


class PDFGenerationError(DocGenError):
    """Raised when PDF generation fails."""
    pass


class InvalidDocumentError(DocGenError):
    """Raised when document data is invalid."""
    pass


class StorageError(DocGenError):
    """Raised when storage operations fail."""
    pass