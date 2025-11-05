from fastapi import FastAPI    #Se importa la librería de FastAPI

app = FastAPI()   #Se establece la app que da inicio al servidor

@app.get("/")   #Se establece el metodo GET en base a buscar la ruta que mostrara el Hola mundo!
def read_root():   #Se define el método que permite leer esta ruta
    return {"mensaje": "¡Hola Mundo!"}  #Se establece el contenido que retorna la ruta
