
import os
import streamlit as st
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from dotenv import load_dotenv
import streamlit.components.v1 as components
import xml.sax.saxutils as saxutils
load_dotenv()
#Variable de entorno 
os.environ['OPENROUTER_API_KEY'] = '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'
#Construccion de modelo 
llm = ChatOpenAI(
    model_name="meta-llama/llama-4-maverick:free",
    openai_api_base="https://openrouter.ai/api/v1",
    openai_api_key=os.environ.get("OPENROUTER_API_KEY"),
    temperature=0.2# mientras mas cercano a dos es mas creativo, pero mientras mas cercano a 0 mas deterministico
)

# Definir un prompt
prompt = PromptTemplate(
    input_variables=["idioma_entrada","idioma_salida","user_input"],
    template="""
            Eres un experto en modelado de procesos. 
            Recibirás una descripción en lenguaje natural y 
            debes devolver una estructura XML clara para generar un diagrama BPMN con la estructura
            de process y bpmndi:BPMNDiagram,
            

            Descripción del usuario:
            {user_input}

            Devuelve solo el XML del proceso BPMN

    """
)
#con las cadenas secuenciales se puede implementar dos consultas en un arrglo
# Crear una cadena de LangChain
chain = LLMChain(llm=llm, prompt=prompt)
st.set_page_config(page_title="Generador BPMN con IA",layout="centered")
st.title("Generador de Procesos BPMN con IA")
descripcion=st.text_area("Describe tu proceso en lenguaje natural:")
if st.button("Generar XML BPMN"):
    if descripcion.strip() == "":
        st.warning("Por favor escribe una descripción del proceso.")
    else:
        with st.spinner("Generando XML..."):
            resultado = chain.run(idioma_entrada='español',idioma_salida='español',user_input=descripcion)
            st.success("✅ Generado exitosamente:")
            st.code(resultado, language="xml")
            st.markdown("### Vista del Diagrama BPMN")
            resultado=resultado.replace('```xml\n','')
            resultado=resultado.replace('\n```','')
            # Cargar la plantilla HTML
            with open("bpmn_viewer.html", "r") as file:
                html_template = file.read()

            # Escapar el XML para inyectarlo en el HTML
            escaped_xml = saxutils.escape(resultado)

            # Reemplazar el marcador {{BPMN_XML}} con el XML escapado
            html_content = html_template.replace("{{BPMN_XML}}", escaped_xml)

            # Renderizar el componente HTML
            components.html(html_content, height=600)

            st.download_button(
                label="📥 Descargar BPMN XML",
                data=resultado,
                file_name="proceso_bpmn.xml",
                mime="application/xml"
            )
            #posible integracion .camunda o un pequeño servicio con Node y implementar agentes con langchain