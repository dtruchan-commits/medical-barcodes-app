import qrcode
from io import BytesIO
import re
from fastapi.responses import Response
from fastapi import HTTPException


def generate_swiss_medical_barcode(gtin: str, lot: str, expiry: str, serial: str = "") -> Response:
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
