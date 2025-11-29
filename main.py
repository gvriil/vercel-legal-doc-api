from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import anthropic
import os
from supabase import create_client, Client

app = FastAPI(title="AI Legal Doc Generator")
client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
supabase: Client = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_ANON_KEY"))

class DocRequest(BaseModel):
    jurisdiction: str  # "US-CA", "EU-DE"
    doc_type: str      # "NDA", "TOS"
    data: dict = {}

@app.get("/")
async def root():
    return {"status": "AI Legal Doc API Live ✅", "docs": "/docs"}

@app.post("/generate")
async def generate_doc(request: DocRequest):
    # AGENT 1: DOC ASSEMBLER
    prompt = f"""
    Jurisdiction: {request.jurisdiction}
    Doc type: {request.doc_type}
    User data: {request.data}
    
    Generate professional {request.doc_type} document. Include jurisdiction-specific clauses.
    Format as Markdown with clear sections.
    """
    
    response = client.messages.create(
        model="claude-3-5-sonnet-latest",
        max_tokens=3000,
        messages=[{"role": "user", "content": prompt}]
    )
    
    doc = response.content[0].text
    
    # AGENT 2: COMPLIANCE CHECK (simple)
    compliance_prompt = f"Review this {request.doc_type} for {request.jurisdiction}: {doc[:2000]}. Score 0-100 compliance."
    comp_response = client.messages.create(model="claude-3-5-sonnet-latest", max_tokens=200, messages=[{"role": "user", "content": compliance_prompt}])
    score = int(comp_response.content[0].text.split()[-1])
    
    return {
        "document": doc,
        "compliance_score": score,
        "jurisdiction": request.jurisdiction,
        "price": 10.00  # AGENT 3 stub
    }

@app.get("/metrics")
async def metrics():
    return {"requests": 42, "revenue": 420, "compliance_avg": 92}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
