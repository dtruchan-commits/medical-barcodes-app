from fastapi import FastAPI, Query
from generators import (
    generate_code128_barcode,
    generate_laetus_barcode,
    generate_swiss_medical_barcode,
    generate_ean13_barcode
)

app = FastAPI(title="Medical Barcode Generator API", version="1.0.0")


@app.get("/")
async def root():
    return {
        "message": "Welcome to the Medical Barcode Generator API",
        "documentation": "/docs",
        "examples": "/examples",
        "health": "/health",
    }


@app.get("/examples")
async def get_examples():
    """Get example usage for all barcode generation endpoints"""
    return {
        "code128": {
            "description": "Generate Code128 barcode for general medical use",
            "endpoint": "/generate/code128",
            "examples": [
                {
                    "url": "/generate/code128?data=MED123456&width=2&height=30",
                    "description": "Basic medical item code",
                },
                {
                    "url": "/generate/code128?data=SAMPLE-2024-001&width=3&height=40",
                    "description": "Sample tracking code with custom size",
                },
            ],
        },
        "laetus": {
            "description": "Generate Laetus-style laboratory barcode",
            "endpoint": "/generate/laetus",
            "format": "LAB-PATIENTID-SAMPLEID",
            "examples": [
                {
                    "url": "/generate/laetus?patient_id=P001&sample_id=S123&lab_code=LAB",
                    "description": "Standard lab sample barcode",
                    "result_data": "LAB-P001-S123",
                },
                {
                    "url": "/generate/laetus?patient_id=PATIENT456&sample_id=BLOOD001&lab_code=HEMA",
                    "description": "Hematology lab sample",
                    "result_data": "HEMA-PATIENT456-BLOOD001",
                },
            ],
        },
        "swiss_medical": {
            "description": "Generate Swiss Medical Code (GS1 compliant QR code)",
            "endpoint": "/generate/swiss-medical",
            "format": "(01)GTIN(10)LOT(17)EXPIRY(21)SERIAL",
            "examples": [
                {
                    "url": "/generate/swiss-medical?gtin=07680001234567&lot=ABC123&expiry=251201",
                    "description": "Basic pharmaceutical product code",
                    "result_data": "(01)07680001234567(10)ABC123(17)251201",
                },
                {
                    "url": "/generate/swiss-medical?gtin=07680009876543&lot=LOT456&expiry=241130&serial=SN789",
                    "description": "Product with serial number",
                    "result_data": "(01)07680009876543(10)LOT456(17)241130(21)SN789",
                },
            ],
            "notes": [
                "GTIN must be 14 digits",
                "Expiry date format: YYMMDD",
                "Serial number is optional",
            ],
        },
        "ean13": {
            "description": "Generate EAN13 barcode for medical products",
            "endpoint": "/generate/ean13",
            "examples": [
                {
                    "url": "/generate/ean13?code=4012345678901",
                    "description": "13-digit EAN code",
                },
                {
                    "url": "/generate/ean13?code=401234567890",
                    "description": "12-digit code (check digit calculated automatically)",
                },
            ],
        },
        "usage_notes": {
            "response_format": "All endpoints return PNG images",
            "content_type": "image/png",
            "error_handling": "Returns 400 status with error details for invalid input",
            "filename": "Images include descriptive filenames in Content-Disposition header",
        },
    }


@app.get("/generate/code128")
async def generate_code128(
    data: str = Query(..., description="Data to encode"),
    width: int = Query(2, description="Bar width"),
    height: int = Query(30, description="Bar height"),
):
    """Generate Code128 barcode (commonly used for medical applications)"""
    return generate_code128_barcode(data, width, height)


@app.get("/generate/laetus")
async def generate_laetus(
    patient_id: str = Query(..., description="Patient ID"),
    sample_id: str = Query(..., description="Sample ID"),
    lab_code: str = Query(default="LAB", description="Laboratory code"),
):
    """Generate Laetus-style medical barcode"""
    return generate_laetus_barcode(patient_id, sample_id, lab_code)


@app.get("/generate/swiss-medical")
async def generate_swiss_medical_code(
    gtin: str = Query(..., description="GTIN (Global Trade Item Number)"),
    lot: str = Query(..., description="Lot number"),
    expiry: str = Query(..., description="Expiry date (YYMMDD)"),
    serial: str = Query(default="", description="Serial number (optional)"),
):
    """Generate Swiss Medical Code (GS1 DataMatrix)"""
    return generate_swiss_medical_barcode(gtin, lot, expiry, serial)


@app.get("/generate/ean13")
async def generate_ean13(
    code: str = Query(..., description="EAN13 code (12 or 13 digits)")
):
    """Generate EAN13 barcode for medical products"""
    return generate_ean13_barcode(code)


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "Medical Barcode Generator"}