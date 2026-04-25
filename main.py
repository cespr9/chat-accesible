import streamlit as st
import os
import base64
from dotenv import load_dotenv
from groq import Groq  

load_dotenv()
api_key = os.getenv("GROQ_API_KEY")
client = Groq(api_key=api_key)

def codificar_imagen(archivo_subido):
    return base64.b64encode(archivo_subido.read()).decode('utf-8')

# Le damos un título chulo para cuando lo vea el reclutador
st.set_page_config(page_title="AI Eyes", page_icon="👁️")
# --- TRUCO CSS PARA CAMBIAR EL TEXTO DEL BOTÓN ---
# --- TRUCO CSS PARA TRADUCIR EL FILE UPLOADER COMPLETO ---
st.markdown("""
    <style>
    /* 1. Botón "Browse files" -> "Subir imagen" */
    div[data-testid="stFileUploader"] section button span::after {
        content: "Subir imagen";
        font-size: 10px;
    }
    div[data-testid="stFileUploader"] section button span {
        font-size: 0px;
    }
    
    /* 2. Texto "Drag and drop file here" -> "o arrastra y suelta la foto aquí" */
    div[data-testid="stFileUploadDropzone"] > div > div > span {
        font-size: 0px;
    }
    div[data-testid="stFileUploadDropzone"] > div > div > span::after {
        content: "o arrastra y suelta la foto aquí";
        font-size: 15px;
    }

    /* 3. Límite de tamaño "Limit 200MB per file" -> "Límite: 200MB" */
    div[data-testid="stFileUploadDropzone"] > div > small {
        font-size: 0px;
    }
    div[data-testid="stFileUploadDropzone"] > div > small::after {
        content: "Límite: 200MB";
        font-size: 13px;
    }
    </style>
""", unsafe_allow_html=True)
st.title("Descriptor de Entorno con IA")
st.write("Seleccionar un archivo y te describiré lo que aparece, dando contexto histórico en caso de que lo identifique.")

# El botón para subir archivos desde la galería o el ordenador
foto = st.file_uploader("Sube una foto de tu galería", type=["jpg", "jpeg", "png"])

# Si el usuario sube una foto, entramos aquí directamente
if foto:
    # Mostramos la imagen en pantalla para confirmar qué se ha subido
    st.image(foto, caption="Imagen seleccionada", use_container_width=True)
    
    # 1. Convertimos la imagen
    # 1. Convertimos la imagen
    imagen_base64 = codificar_imagen(foto)
    
    # 2. El nuevo prompt adaptado a la idea de tu padre
    prompt_sistema = """Eres los ojos de una persona con discapacidad visual severa. Tu objetivo es describir la imagen adjunta de forma útil.
    1. Describe la escena general, el paisaje, el entorno o los objetos principales de forma clara y concisa.
    2. SI (y solo si) identificas un monumento, edificio famoso, obra de arte o sitio histórico reconocible, di su nombre y añade un párrafo contando su historia o importancia cultural. Así como otro explicando la construcción del monumento o disposición de las obras
    Sé natural, directo y no uses lenguaje excesivamente robótico.
    En caso de que no sea un monumento o paisaje, informa al usuario que no es contenido relacionado con el propósito de la web"""

    # 3. Ponemos un "cargando" visual para que se sepa que está pensando
    with st.spinner("Analizando el entorno..."):
        # 4. Llamamos a Groq
        response = client.chat.completions.create(
            model="meta-llama/llama-4-scout-17b-16e-instruct", 
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt_sistema},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{imagen_base64}",
                            },
                        },
                    ],
                }
            ],
        )

       # 5. Extraemos la respuesta
        respuesta_ia = response.choices[0].message.content
        st.success("¡Entorno analizado!")
        
        # --- CÓDIGO DE ACCESIBILIDAD AVANZADA PARA VOICEOVER ---
        html_accesible = f"""
        <div id="bloque-respuesta" aria-live="assertive" role="alert" tabindex="-1" style="background-color: #f0f2f6; padding: 20px; border-radius: 10px; margin-top: 20px;">
            <p style="font-size: 18px; color: #31333F;">{respuesta_ia}</p>
        </div>
        <script>
            // Forzamos al navegador a bajar hasta la respuesta y pasarle el foco
            const doc = window.parent.document;
            const elemento = doc.getElementById('bloque-respuesta');
            if(elemento) {{
                elemento.scrollIntoView({{behavior: 'smooth', block: 'center'}});
                elemento.focus();
            }}
        </script>
        """
        st.markdown(html_accesible, unsafe_allow_html=True)