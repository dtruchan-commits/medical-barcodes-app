from typing import Dict, Any
from fastapi import FastAPI, Query, HTTPException
from fastapi.responses import Response
from pydantic import ValidationError
from generators import (
    generate_code128_barcode,
    generate_laetus_barcode,
    generate_swiss_medical_barcode,
    generate_ean13_barcode
)
from models import (
    Code128Request,
    LaetusRequest,
    SwissMedicalRequest,
    EAN13Request,
    ErrorResponse
)
from examples import get_api_examples

app = FastAPI(title="Medical Barcode Generator API", version="1.0.0")


@app.get("/", tags=["System"])
async def root() -> Dict[str, str]:
    return {
        "message": "Welcome to the Medical Barcode Generator API",
        "documentation": "/docs",
        "examples": "/examples",
        "health": "/health",
    }


@app.get("/examples", tags=["System"])
async def get_examples() -> Dict[str, Any]:
    """Get example usage for all barcode generation endpoints"""
    return get_api_examples()


@app.get("/generate/code128", responses={400: {"model": ErrorResponse}}, tags=["Barcode Generation"])
async def generate_code128(
    data: str = Query(..., description="Data to encode"),
    width: int = Query(2, description="Bar width"),
    height: int = Query(30, description="Bar height"),
) -> Response:
    """Generate Code128 barcode (commonly used for medical applications)"""
    try:
        request = Code128Request(data=data, width=width, height=height)
        return generate_code128_barcode(request)
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/generate/laetus", responses={400: {"model": ErrorResponse}}, tags=["Barcode Generation"])
async def generate_laetus(
    patient_id: str = Query(..., description="Patient ID"),
    sample_id: str = Query(..., description="Sample ID"),
    lab_code: str = Query(default="LAB", description="Laboratory code"),
) -> Response:
    """Generate Laetus-style medical barcode"""
    try:
        request = LaetusRequest(patient_id=patient_id, sample_id=sample_id, lab_code=lab_code)
        return generate_laetus_barcode(request)
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/generate/swiss-medical", responses={400: {"model": ErrorResponse}}, tags=["Barcode Generation"])
async def generate_swiss_medical_code(
    gtin: str = Query(..., description="GTIN (Global Trade Item Number)"),
    lot: str = Query(..., description="Lot number"),
    expiry: str = Query(..., description="Expiry date (YYMMDD)"),
    serial: str = Query(default="", description="Serial number (optional)"),
) -> Response:
    """Generate Swiss Medical Code (GS1 DataMatrix)"""
    try:
        request = SwissMedicalRequest(gtin=gtin, lot=lot, expiry=expiry, serial=serial)
        return generate_swiss_medical_barcode(request)
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/generate/ean13", responses={400: {"model": ErrorResponse}}, tags=["Barcode Generation"])
async def generate_ean13(
    code: str = Query(..., description="EAN13 code (12 or 13 digits)")
) -> Response:
    """Generate EAN13 barcode for medical products"""
    try:
        request = EAN13Request(code=code)
        return generate_ean13_barcode(request)
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/health", tags=["System"])
async def health_check() -> Dict[str, str]:
    """Health check endpoint"""
    return {"status": "healthy", "service": "Medical Barcode Generator"}