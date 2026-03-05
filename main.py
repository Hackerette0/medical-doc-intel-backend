from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
from pathlib import Path

app = FastAPI(title="Medical Document Intelligence")

# Allow frontend to connect
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # React default
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class AnalysisResponse(BaseModel):
    key_analysis: list[str]
    tags: dict
    document_type: str

@app.post("/analyze", response_model=AnalysisResponse)
async def analyze_document(file: UploadFile = File(...)):
    if not file.filename.endswith('.pdf'):
        raise HTTPException(400, "Only PDF files allowed")
    
    # TODO: Add your PDF processing logic here
    content = await file.read()
    
    # Placeholder response (we'll implement real logic next)
    return {
        "key_analysis": [
            "Document processed successfully",
            "Text extraction completed",
            "Analysis in progress",
            "Key findings identified",
            "Recommendations generated"
        ],
        "tags": {
            "medicines": [],
            "conditions": [],
            "probable_conditions": [],
            "deficiencies": [],
            "other": []
        },
        "document_type": "unknown"
    }

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)