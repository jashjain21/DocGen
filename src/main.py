from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.responses import StreamingResponse, JSONResponse
from pydantic import ValidationError
import io
from src.schema import Invoice
from src.engine import PDFGenerator
from src.storage import FileManager
from src.exceptions import DocGenError, TemplateError, PDFGenerationError, InvalidDocumentError, StorageError

app = FastAPI(title="DocGen API", description="Offline PDF Report Generator", version="1.0.0")

pdf_generator = PDFGenerator()
file_manager = FileManager()

@app.exception_handler(ValidationError)
async def validation_exception_handler(request: Request, exc: ValidationError):
    return JSONResponse(
        status_code=422,
        content={"error": "Validation error", "details": exc.errors()}
    )

@app.exception_handler(InvalidDocumentError)
async def invalid_document_exception_handler(request: Request, exc: InvalidDocumentError):
    return JSONResponse(
        status_code=400,
        content={"error": "Invalid document", "message": str(exc)}
    )

@app.exception_handler(TemplateError)
async def template_exception_handler(request: Request, exc: TemplateError):
    return JSONResponse(
        status_code=500,
        content={"error": "Template error", "message": str(exc)}
    )

@app.exception_handler(PDFGenerationError)
async def pdf_generation_exception_handler(request: Request, exc: PDFGenerationError):
    return JSONResponse(
        status_code=500,
        content={"error": "PDF generation error", "message": str(exc)}
    )

@app.exception_handler(StorageError)
async def storage_exception_handler(request: Request, exc: StorageError):
    return JSONResponse(
        status_code=500,
        content={"error": "Storage error", "message": str(exc)}
    )

@app.exception_handler(DocGenError)
async def general_docgen_exception_handler(request: Request, exc: DocGenError):
    return JSONResponse(
        status_code=500,
        content={"error": "DocGen error", "message": str(exc)}
    )

@app.post("/generate")
async def generate_pdf(
    invoice: Invoice,
    page_size: str = Query("a4", enum=["a4", "letter", "legal"]),
    orientation: str = Query("portrait", enum=["portrait", "landscape"]),
    margins: str = Query("10mm"),
    title: str = Query(""),
    author: str = Query("DocGen"),
    save_to_disk: bool = Query(False)
):
    try:
        pdf_bytes = pdf_generator.generate_pdf(
            "invoice.html",
            invoice,
            page_size=page_size,
            margins=margins,
            orientation=orientation,
            title=title or f"Invoice {invoice.invoice_number}",
            author=author
        )
        if save_to_disk:
            filename = f"{invoice.invoice_number}.pdf"
            file_manager.save_pdf(pdf_bytes, filename, {
                'invoice_number': invoice.invoice_number,
                'customer_name': invoice.customer.name,
                'total_amount': invoice.total_amount
            })

        # Return PDF as download
        return StreamingResponse(
            io.BytesIO(pdf_bytes),
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename={invoice.invoice_number}.pdf"}
        )
    except ValidationError:
        raise  # Handled by exception handler
    except Exception as e:
        raise PDFGenerationError(f"PDF generation failed: {str(e)}")

@app.get("/documents")
async def list_documents(
    year: int = Query(None),
    month: int = Query(None),
    invoice_number: str = Query(None)
):
    try:
        documents = file_manager.list_reports(year=year, month=month, invoice_number=invoice_number)
        return {"documents": documents}
    except Exception as e:
        raise StorageError(f"Failed to list documents: {str(e)}")

@app.get("/document/{filename}")
async def download_document(filename: str):
    try:
        content = file_manager.get_report_content(filename)
        if content is None:
            raise HTTPException(status_code=404, detail="Document not found")
        return StreamingResponse(
            io.BytesIO(content),
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
    except HTTPException:
        raise
    except Exception as e:
        raise StorageError(f"Failed to retrieve document: {str(e)}")

@app.delete("/document/{filename}")
async def delete_document(filename: str):
    try:
        success = file_manager.delete_report(filename)
        if not success:
            raise HTTPException(status_code=404, detail="Document not found")
        return {"message": f"Document {filename} deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise StorageError(f"Failed to delete document: {str(e)}")

@app.get("/health")
async def health_check():
    try:
        documents = file_manager.list_reports()
        return {
            "status": "healthy",
            "document_count": len(documents),
            "service": "DocGen API"
        }
    except Exception as e:
        raise StorageError(f"Health check failed: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)