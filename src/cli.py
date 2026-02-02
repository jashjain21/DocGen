import argparse
import json
import os
import sys
from pathlib import Path
from typing import List

from tqdm import tqdm
from pydantic import ValidationError

from src.schema import Invoice
from src.engine import PDFGenerator
from src.storage import FileManager


def generate_pdf(json_file: str, output_file: str = None):
    """Generate PDF from JSON file."""
    try:
        with open(json_file, 'r') as f:
            data = json.load(f)
        invoice = Invoice(**data)
        generator = PDFGenerator()
        pdf_bytes = generator.generate_pdf("invoice.html", invoice)
        if output_file is None:
            output_file = f"{invoice.invoice_number}.pdf"
        with open(output_file, 'wb') as f:
            f.write(pdf_bytes)
        print(f"PDF generated: {output_file}")
    except FileNotFoundError:
        print(f"Error: JSON file '{json_file}' not found.")
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in '{json_file}': {e}")
    except ValidationError as e:
        print(f"Error: Invalid invoice data in '{json_file}': {e}")
    except Exception as e:
        print(f"Error generating PDF from '{json_file}': {e}")


def batch_generate(folder: str):
    """Batch generate PDFs from all JSON files in folder."""
    folder_path = Path(folder)
    if not folder_path.exists():
        print(f"Error: Folder '{folder}' does not exist.")
        return

    json_files = list(folder_path.glob("*.json"))
    if not json_files:
        print(f"No JSON files found in '{folder}'.")
        return

    generator = PDFGenerator()
    successful = []
    failed = []

    with tqdm(total=len(json_files), desc="Processing JSON files") as pbar:
        for json_file in json_files:
            try:
                with open(json_file, 'r') as f:
                    data = json.load(f)
                invoice = Invoice(**data)
                pdf_bytes = generator.generate_pdf("invoice.html", invoice)
                output_file = folder_path / f"{invoice.invoice_number}.pdf"
                with open(output_file, 'wb') as f:
                    f.write(pdf_bytes)
                successful.append(str(json_file))
            except Exception as e:
                failed.append((str(json_file), str(e)))
            pbar.update(1)

    print(f"\nBatch processing complete.")
    print(f"Successful: {len(successful)}")
    print(f"Failed: {len(failed)}")
    if failed:
        print("Failed files:")
        for file, error in failed:
            print(f"  - {file}: {error}")


def list_documents(year: int = None, month: int = None, invoice_number: str = None):
    """List generated documents from manifest."""
    manager = FileManager()
    documents = manager.list_reports(year=year, month=month, invoice_number=invoice_number)
    if not documents:
        print("No documents found.")
        return

    print(f"Total documents: {len(documents)}")
    for doc in documents:
        print(f"- {doc['filename']} ({doc['generated_at'][:10]}) - {doc['invoice_number']}")


def main():
    parser = argparse.ArgumentParser(description="DocGen CLI")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Generate command
    gen_parser = subparsers.add_parser("generate", help="Generate PDF from JSON file")
    gen_parser.add_argument("json_file", help="Path to JSON file")
    gen_parser.add_argument("-o", "--output", help="Output PDF file name")

    # Batch command
    batch_parser = subparsers.add_parser("batch", help="Batch generate PDFs from JSON files in folder")
    batch_parser.add_argument("folder", help="Folder containing JSON files")

    # List command
    list_parser = subparsers.add_parser("list", help="List generated documents")
    list_parser.add_argument("-y", "--year", type=int, help="Filter by year")
    list_parser.add_argument("-m", "--month", type=int, help="Filter by month")
    list_parser.add_argument("-i", "--invoice", help="Filter by invoice number")

    args = parser.parse_args()

    if args.command == "generate":
        generate_pdf(args.json_file, args.output)
    elif args.command == "batch":
        batch_generate(args.folder)
    elif args.command == "list":
        list_documents(args.year, args.month, args.invoice)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()