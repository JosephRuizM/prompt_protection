from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import numpy as np
import chromadb
from chromadb.utils import embedding_functions
import motor_firewall

app = FastAPI()

modelo_emb = embedding_functions.DefaultEmbeddingFunction()
chroma_client = chromadb.Client()

collection = chroma_client.get_or_create_collection(name="known_attacks")

class PromptRequest(BaseModel):
    prompt: str

@app.post("/login")
def enviar(request: PromptRequest):
    prompt_usuario = request.prompt

    vector_actual = modelo_emb([prompt_usuario])[0]
    array_actual = np.array(vector_actual, dtype=np.float32).flatten()

    resultados = collection.query(
        query_texts=[prompt_usuario],
        n_results=3,
        include=["embeddings"]
    )

    if not resultados or not resultados.get("embeddings") or len(resultados["embeddings"]) == 0:
        return {"status": "Seguro", "mensaje": "Prompt verificado con éxito (No hay firmas de ataque registrados)."}

    vectores_sospechosos = resultados["embeddings"][0]
    
    if len(vectores_sospechosos) == 0:
        return {"status": "Seguro", "mensaje": "Prompt verificado con éxito."}
        
    array_sospechosos = np.array(vectores_sospechosos, dtype=np.float32)

    try:
        es_ataque = motor_firewall.evaluar_prompt(array_actual, array_sospechosos)
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=f"Error de dimensiones en el motor C++: {str(e)}")

    if es_ataque:
        raise HTTPException(status_code=403, detail="Prompt bloqueado: Intento de Inyección detectado.")

    return {"status": "Seguro", "mensaje": "Prompt verificado con éxito."}

