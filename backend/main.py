from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import Response
import barcode
from barcode.writer import ImageWriter
import qrcode
from io import BytesIO
import re

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
    try:
        code128 = barcode.get_barcode_class("code128")
        barcode_instance = code128(data, writer=ImageWriter())

        buffer = BytesIO()
        barcode_instance.write(
            buffer,
            options={
                "module_width": width / 10,
                "module_height": height,
                "text_distance": 5,
                "font_size": 10,
            },
        )
        buffer.seek(0)

        return Response(
            content=buffer.getvalue(),
            media_type="image/png",
            headers={"Content-Disposition": f"inline; filename=barcode_{data}.png"},
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error generating barcode: {str(e)}")


@app.get("/generate/laetus")
async def generate_laetus_barcode(
    patient_id: str = Query(..., description="Patient ID"),
    sample_id: str = Query(..., description="Sample ID"),
    lab_code: str = Query(default="LAB", description="Laboratory code"),
):
    """Generate Laetus-style medical barcode"""
    try:
        # Laetus format: LAB-PATIENTID-SAMPLEID
        laetus_data = f"{lab_code}-{patient_id}-{sample_id}"

        # Validate format
        if not re.match(r"^[A-Z0-9]+-[A-Z0-9]+-[A-Z0-9]+$", laetus_data):
            raise ValueError("Invalid Laetus format")

        code128 = barcode.get_barcode_class("code128")
        barcode_instance = code128(laetus_data, writer=ImageWriter())

        buffer = BytesIO()
        barcode_instance.write(
            buffer,
            options={
                "module_width": 0.2,
                "module_height": 15,
                "text_distance": 5,
                "font_size": 10,
            },
        )
        buffer.seek(0)

        return Response(
            content=buffer.getvalue(),
            media_type="image/png",
            headers={"Content-Disposition": f"inline; filename=laetus_{laetus_data}.png"},
        )
    except Exception as e:
        raise HTTPException(
            status_code=400, detail=f"Error generating Laetus barcode: {str(e)}"
        )


@app.get("/generate/swiss-medical")
async def generate_swiss_medical_code(
    gtin: str = Query(..., description="GTIN (Global Trade Item Number)"),
    lot: str = Query(..., description="Lot number"),
    expiry: str = Query(..., description="Expiry date (YYMMDD)"),
    serial: str = Query(default="", description="Serial number (optional)"),
):
    """Generate Swiss Medical Code (GS1 DataMatrix)"""
    try:
        # Validate GTIN (should be 14 digits)
        if not re.match(r"^\d{14}$", gtin):
            raise ValueError("GTIN must be 14 digits")

        # Validate expiry date format
        if not re.match(r"^\d{6}$", expiry):
            raise ValueError("Expiry date must be YYMMDD format")

        # Build GS1 format string
        gs1_data = f"(01){gtin}(10){lot}(17){expiry}"
        if serial:
            gs1_data += f"(21){serial}"

        # Generate QR code (DataMatrix alternative using QR)
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=4,
            border=2,
        )
        qr.add_data(gs1_data)
        qr.make(fit=True)

        img = qr.make_image(fill_color="black", back_color="white")

        buffer = BytesIO()
        img.save(buffer, format="PNG")
        buffer.seek(0)

        return Response(
            content=buffer.getvalue(),
            media_type="image/png",
            headers={"Content-Disposition": f"inline; filename=swiss_medical_{gtin}.png"},
        )
    except Exception as e:
        raise HTTPException(
            status_code=400, detail=f"Error generating Swiss Medical code: {str(e)}"
        )


@app.get("/generate/ean13")
async def generate_ean13(
    code: str = Query(..., description="EAN13 code (12 or 13 digits)")
):
    """Generate EAN13 barcode for medical products"""
    try:
        # Validate EAN13 format
        if not re.match(r"^\d{12,13}$", code):
            raise ValueError("EAN13 must be 12 or 13 digits")

        ean13 = barcode.get_barcode_class("ean13")
        barcode_instance = ean13(code[:12], writer=ImageWriter())

        buffer = BytesIO()
        barcode_instance.write(
            buffer,
            options={
                "module_width": 0.33,
                "module_height": 25,
                "text_distance": 5,
                "font_size": 12,
            },
        )
        buffer.seek(0)

        return Response(
            content=buffer.getvalue(),
            media_type="image/png",
            headers={"Content-Disposition": f"inline; filename=ean13_{code}.png"},
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error generating EAN13 barcode: {str(e)}")


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "Medical Barcode Generator"}