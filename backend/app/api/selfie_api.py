from threading import BoundedSemaphore
from typing import Literal
from fastapi import APIRouter, File, Form, UploadFile, HTTPException
from app.services.selfie_avatar import avatar_status, generate_avatar
from app.services.tryon_service import MAX_BYTES, TryOnError

router = APIRouter(prefix="/mvp/ia/avatar", tags=["Avatar por selfie experimental"])
slots = BoundedSemaphore(1)

@router.get("/status")
def status():
    return avatar_status()

@router.post("")
def avatar(consent: bool = Form(...), template: Literal["masculino", "feminino"] = Form("masculino"), selfie: UploadFile = File(...)):
    try:
        if not consent: raise HTTPException(422, "Autorize o processamento local da selfie.")
        if not slots.acquire(blocking=False): raise HTTPException(429, "Já existe um avatar sendo gerado. Aguarde.")
        try:
            return generate_avatar(selfie.file.read(MAX_BYTES + 1), template)
        except TryOnError as error:
            raise HTTPException(error.status, error.message) from error
        finally:
            slots.release()
    finally:
        selfie.file.close()
