from fastapi import APIRouter, Depends, File, UploadFile
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.models import User
from app.schemas import PracticeCompleteRequest, PracticeCompleteResponse, PracticeGenerateResponse
from app.services.practice_service import (
    add_practice_point,
    calculate_practice_point,
    generate_sentences_from_pdf_mock,
)


router = APIRouter(prefix="/api/practice", tags=["practice"])


@router.post("/generate", response_model=PracticeGenerateResponse)
async def generate_practice_sentences(
    file: UploadFile = File(...),
    _: User = Depends(get_current_user),
):
    pdf_bytes = await file.read()
    sentences = generate_sentences_from_pdf_mock(pdf_bytes)
    return PracticeGenerateResponse(sentences=sentences)


@router.post("/complete", response_model=PracticeCompleteResponse)
def complete_practice(
    request: PracticeCompleteRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    earned_point = calculate_practice_point(
        request.completed_count,
        request.accuracy,
        request.speed,
    )
    add_practice_point(current_user, earned_point)
    db.commit()
    db.refresh(current_user)
    return PracticeCompleteResponse(earned_point=earned_point, total_point=current_user.point)
