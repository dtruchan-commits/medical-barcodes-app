from typing import Any, Dict
import barcode
from barcode.writer import ImageWriter
from io import BytesIO
from fastapi.responses import Response
from fastapi import HTTPException
from models.barcode_models import LaetusRequest


def generate_laetus_barcode(request: LaetusRequest) -> Response:
    """Generate Laetus-style medical barcode"""
    try:
        # Laetus format: LAB-PATIENTID-SAMPLEID
        laetus_data: str = f"{request.lab_code}-{request.patient_id}-{request.sample_id}"

        code128 = barcode.get_barcode_class("code128")
        barcode_instance = code128(laetus_data, writer=ImageWriter())

        buffer = BytesIO()
        options: Dict[str, Any] = {
            "module_width": 0.2,
            "module_height": 15,
            "text_distance": 5,
            "font_size": 10,
        }
        barcode_instance.write(buffer, options=options)
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
