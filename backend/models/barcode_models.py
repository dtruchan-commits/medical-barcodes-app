from typing import Optional, Dict, Any
from pydantic import BaseModel, Field, validator
import re


class BarcodeRequest(BaseModel):
    """Base barcode request model"""
    pass


class Code128Request(BarcodeRequest):
    """Code128 barcode generation request"""
    data: str = Field(..., description="Data to encode", min_length=1)
    width: int = Field(2, description="Bar width", ge=1, le=10)
    height: int = Field(30, description="Bar height", ge=10, le=100)


class LaetusRequest(BarcodeRequest):
    """Laetus barcode generation request"""
    patient_id: str = Field(..., description="Patient ID", min_length=1)
    sample_id: str = Field(..., description="Sample ID", min_length=1)
    lab_code: str = Field("LAB", description="Laboratory code", min_length=1)
    
    @validator('patient_id', 'sample_id', 'lab_code')
    def validate_alphanumeric(cls, v):
        if not re.match(r'^[A-Z0-9]+$', v):
            raise ValueError('Must contain only uppercase letters and numbers')
        return v


class SwissMedicalRequest(BarcodeRequest):
    """Swiss Medical Code generation request"""
    gtin: str = Field(..., description="GTIN (Global Trade Item Number)")
    lot: str = Field(..., description="Lot number", min_length=1)
    expiry: str = Field(..., description="Expiry date (YYMMDD)")
    serial: Optional[str] = Field("", description="Serial number (optional)")
    
    @validator('gtin')
    def validate_gtin(cls, v):
        if not re.match(r'^\d{14}$', v):
            raise ValueError('GTIN must be exactly 14 digits')
        return v
    
    @validator('expiry')
    def validate_expiry(cls, v):
        if not re.match(r'^\d{6}$', v):
            raise ValueError('Expiry date must be YYMMDD format (6 digits)')
        return v


class EAN13Request(BarcodeRequest):
    """EAN13 barcode generation request"""
    code: str = Field(..., description="EAN13 code (12 or 13 digits)")
    
    @validator('code')
    def validate_ean13(cls, v):
        if not re.match(r'^\d{12,13}$', v):
            raise ValueError('EAN13 must be 12 or 13 digits')
        return v


class BarcodeResponse(BaseModel):
    """Barcode generation response"""
    success: bool = Field(True, description="Generation success status")
    data: Optional[str] = Field(None, description="Encoded data")
    format: str = Field(..., description="Barcode format")
    filename: str = Field(..., description="Generated filename")


class ErrorResponse(BaseModel):
    """Error response model"""
    success: bool = Field(False, description="Success status")
    error: str = Field(..., description="Error message")
    detail: Optional[str] = Field(None, description="Error details")
