from typing import Any
import qrcode
from qrcode.image.pil import PilImage
from io import BytesIO
from fastapi.responses import Response
from fastapi import HTTPException
from models.barcode_models import SwissMedicalRequest


def generate_swiss_medical_barcode(request: SwissMedicalRequest) -> Response:
    """Generate Swiss Medical Code (GS1 DataMatrix)"""
    try:
        # Build GS1 format string
        gs1_data: str = f"(01){request.gtin}(10){request.lot}(17){request.expiry}"
        if request.serial:
            gs1_data += f"(21){request.serial}"

        # Generate QR code (DataMatrix alternative using QR)
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=4,
            border=2,
        )
        qr.add_data(gs1_data)
        qr.make(fit=True)

        img: PilImage = qr.make_image(fill_color="black", back_color="white")

        buffer = BytesIO()
        img.save(buffer, format="PNG")
        buffer.seek(0)

        return Response(
            content=buffer.getvalue(),
            media_type="image/png",
            headers={"Content-Disposition": f"inline; filename=swiss_medical_{request.gtin}.png"},
        )
    except Exception as e:
        raise HTTPException(
            status_code=400, detail=f"Error generating Swiss Medical code: {str(e)}"
        )
