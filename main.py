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
st.title("Descriptor de Entorno con IA")
st.write("Seleccionar un archivo y te describiré lo que aparece, dando contexto histórico en caso de que lo identifique.")

# El botón para subir archivos desde la galería o el ordenador
foto = st.file_uploader("Sube una foto de tu galería", type=["jpg", "jpeg", "png"])

# Si el usuario sube una foto, entramos aquí directamente
# Si el usuario sube una foto, entramos aquí directamente
if foto:
    # Mostramos la imagen en pantalla
    st.image(foto, caption="Imagen seleccionada", use_container_width=True)
    
    # --- LA MAGIA: Comprobamos si esta foto es nueva o si ya la habíamos procesado ---
    if "ultimo_archivo" not in st.session_state or st.session_state["ultimo_archivo"] != foto.file_id:
        
        imagen_base64 = codificar_imagen(foto)
        
        prompt_sistema = """Eres los ojos de una persona con discapacidad visual severa. Tu objetivo es describir la imagen adjunta de forma útil.
        1. Describe la escena general, el paisaje, el entorno o los objetos principales de forma clara y concisa.
        2. SI (y solo si) identificas un monumento, edificio famoso, obra de arte o sitio histórico reconocible, di su nombre y añade un párrafo contando su historia o importancia cultural. Así como otro explicando la construcción del monumento o disposición de las obras.
        Sé natural, directo y no uses lenguaje excesivamente robótico.
        En caso de que no sea un monumento o paisaje, informa al usuario que no es contenido relacionado con el propósito de la web."""

        with st.spinner("Analizando el entorno..."):
            response = client.chat.completions.create(
                model="meta-llama/llama-4-scout-17b-16e-instruct", 
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt_sistema},
                            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{imagen_base64}"}},
                        ],
                    }
                ],
            )

            # Guardamos la respuesta original y el "DNI" de la foto en la memoria
            st.session_state["texto_original"] = response.choices[0].message.content
            st.session_state["ultimo_archivo"] = foto.file_id
            
        st.success("¡Entorno analizado!")

    # 1. PINTAMOS EL TEXTO ORIGINAL SIEMPRE (Sacado de la memoria, no de la IA)
    html_accesible = f"""
    <div id="bloque-respuesta" aria-live="assertive" role="alert" tabindex="-1" style="background-color: #f0f2f6; padding: 20px; border-radius: 10px; margin-top: 20px;">
        <p style="font-size: 18px; color: #31333F;">{st.session_state["texto_original"]}</p>
    </div>
    <script>
        const doc = window.parent.document;
        const elemento = doc.getElementById('bloque-respuesta');
        if(elemento) {{
            elemento.scrollIntoView({{behavior: 'smooth', block: 'center'}});
            elemento.focus();
        }}
    </script>
    """
    st.markdown(html_accesible, unsafe_allow_html=True)

    # 2. SECCIÓN DE LECTURA FÁCIL
    st.write("---")
    
    if st.button("Adaptar descripción a lectura fácil", use_container_width=True):
        with st.spinner("Simplificando el texto..."):
            prompt_lectura_facil = f"""
            Pasa este texto a Lectura Fácil.
            Texto original:
            {st.session_state["texto_original"]}
            Escribe la respuesta usando SOLO viñetas.
            """
            
            response_lf = client.chat.completions.create(
                model="llama-3.1-8b-instant", 
                temperature=0.1, 
                messages=[
                    {
                        "role": "system", 
                        "content": "Eres un adaptador de textos a Lectura Fácil. Tienes prohibido escribir párrafos. Tienes prohibido usar nombres de arquitectos, siglos o fechas exactas. Solo puedes responder con viñetas cortas, directas y con vocabulario de primaria."
                    },
                    {
                        "role": "user", 
                        "content": prompt_lectura_facil
                    }
                ]
            )
            
            texto_simplificado = response_lf.choices[0].message.content
            st.success("✨ Texto adaptado a Lectura Fácil:")

            html_facil = f"""
            <div id="bloque-facil" aria-live="assertive" role="alert" tabindex="-1" style="background-color: #e8f5e9; padding: 20px; border-radius: 10px; border-left: 5px solid #4caf50; margin-top: 20px;">
                <p style="font-size: 22px; color: #1b5e20; line-height: 1.5;">{texto_simplificado}</p>
            </div>
            <script>
                const doc2 = window.parent.document;
                const elemento2 = doc2.getElementById('bloque-facil');
                if(elemento2) {{
                    elemento2.scrollIntoView({{behavior: 'smooth', block: 'center'}});
                    elemento2.focus();
                }}
            </script>
            """
            st.markdown(html_facil, unsafe_allow_html=True)