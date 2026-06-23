from fastapi import FastAPI, HTTPException
import numpy as np
import chromadb
from chromadb.utils import embedding_functions


import motor_firewall

app = FastAPI()
modelo_emb = embedding_functions.DefaultEmbeddingFunction()
chroma_client = chromadb.Client()
collection = chroma_client.get_or_create_collection(name="firewall_logs")


@app.post("/login")
def enviar(datos: dict):
    prompt_usuario = datos["prompt"]

  
    vector_actual = modelo_emb([prompt_usuario])[0]

    
    resultados = collection.query(
        query_texts=[prompt_usuario],
        n_results=3,
        include=["embeddings"]
    )

   
    vectores_sospechosos = resultados["embeddings"]

    
    array_actual = np.array(vector_actual, dtype=np.float32)
    array_sospechosos = np.array(vectores_sospechosos, dtype=np.float32)

    
    es_ataque = motor_firewall.evaluar_prompt(array_actual, array_sospechosos)

    if es_ataque:
  
        raise HTTPException(status_code=403, detail="Prompt bloqueado: Intento de Inyección detectado.")

    return {"status": "Seguro", "mensaje": "Prompt verificado con éxito."}
