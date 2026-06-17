from fastapi import FastAPI, HTTPException
import numpy as np
import chromadb
from chromadb.utils import embedding_functions

# IMPORTAS TU MÓDULO HECHO EN C++
import motor_firewall

app = FastAPI()
modelo_emb = embedding_functions.DefaultEmbeddingFunction()
chroma_client = chromadb.Client()
collection = chroma_client.get_or_create_collection(name="firewall_logs")


@app.post("/login")
def enviar(datos: dict):
    prompt_usuario = datos["prompt"]

    # 1. Vectorizar el prompt actual (Mantiene el [0] porque es un solo vector plano)
    vector_actual = modelo_emb([prompt_usuario])[0]

    # 2. Consultar la base de datos vectorial
    resultados = collection.query(
        query_texts=[prompt_usuario],
        n_results=3,
        include=["embeddings"]
    )

    # CORREGIDO: Removemos el [0] para enviar la matriz completa de 3 vectores sospechosos a C++
    vectores_sospechosos = resultados["embeddings"]

    # 3. Transformar a NumPy con float32 (Coincidencia exacta con el float* de C++)
    array_actual = np.array(vector_actual, dtype=np.float32)
    array_sospechosos = np.array(vectores_sospechosos, dtype=np.float32)

    # 4. PASAR EL CONTROL A C++
    # C++ procesa la matriz en microsegundos y nos devuelve un booleano puro
    es_ataque = motor_firewall.evaluar_prompt(array_actual, array_sospechosos)

    if es_ataque:
        # Bloqueo inmediato si superó el 85% de similitud coseno
        raise HTTPException(status_code=403, detail="Prompt bloqueado: Intento de Inyección detectado.")

    return {"status": "Seguro", "mensaje": "Prompt verificado con éxito."}
