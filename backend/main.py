from typing import Dict, Any
from fastapi import FastAPI, Query
from fastapi.responses import Response
from generators import (
    generate_code128_barcode,
    generate_laetus_barcode,
    generate_swiss_medical_barcode,
    generate_ean13_barcode
)
from examples import get_api_examples

app = FastAPI(title="Medical Barcode Generator API", version="1.0.0")


@app.get("/")
async def root() -> Dict[str, str]:
    return {
        "message": "Welcome to the Medical Barcode Generator API",
        "documentation": "/docs",
        "examples": "/examples",
        "health": "/health",
    }


@app.get("/examples")
async def get_examples() -> Dict[str, Any]:
    """Get example usage for all barcode generation endpoints"""
    return get_api_examples()


@app.get("/generate/code128")
async def generate_code128(
    data: str = Query(..., description="Data to encode"),
    width: int = Query(2, description="Bar width"),
    height: int = Query(30, description="Bar height"),
) -> Response:
    """Generate Code128 barcode (commonly used for medical applications)"""
    return generate_code128_barcode(data, width, height)


@app.get("/generate/laetus")
async def generate_laetus(
    patient_id: str = Query(..., description="Patient ID"),
    sample_id: str = Query(..., description="Sample ID"),
    lab_code: str = Query(default="LAB", description="Laboratory code"),
) -> Response:
    """Generate Laetus-style medical barcode"""
    return generate_laetus_barcode(patient_id, sample_id, lab_code)


@app.get("/generate/swiss-medical")
async def generate_swiss_medical_code(
    gtin: str = Query(..., description="GTIN (Global Trade Item Number)"),
    lot: str = Query(..., description="Lot number"),
    expiry: str = Query(..., description="Expiry date (YYMMDD)"),
    serial: str = Query(default="", description="Serial number (optional)"),
) -> Response:
    """Generate Swiss Medical Code (GS1 DataMatrix)"""
    return generate_swiss_medical_barcode(gtin, lot, expiry, serial)


@app.get("/generate/ean13")
async def generate_ean13(
    code: str = Query(..., description="EAN13 code (12 or 13 digits)")
) -> Response:
    """Generate EAN13 barcode for medical products"""
    return generate_ean13_barcode(code)


@app.get("/health")
async def health_check() -> Dict[str, str]:
    """Health check endpoint"""
    return {"status": "healthy", "service": "Medical Barcode Generator"}