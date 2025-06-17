
import os
import streamlit as st
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from dotenv import load_dotenv
import json
import re
load_dotenv()

def json_to_bpmn_xml(data):
    xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<bpmn:definitions xmlns:bpmn="http://www.omg.org/spec/BPMN/20100524/MODEL"
                  xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
                  id="Definitions_1" targetNamespace="http://bpmn.io/schema/bpmn">
  <bpmn:process id="{data['process'].get('id', 'Process_1')}" name="{data['process'].get('name', 'Proceso')}" isExecutable="true">
"""

    # Mapear nodos con sus IDs
    for node in data["process"]["nodes"]:
        node_id = node["id"]
        node_name = node["name"]
        node_type = node["type"]

        if node_type == "startEvent":
            xml += f'    <bpmn:startEvent id="{node_id}" name="{node_name}" />\n'
        elif node_type == "endEvent":
            xml += f'    <bpmn:endEvent id="{node_id}" name="{node_name}" />\n'
        elif node_type == "task":
            xml += f'    <bpmn:task id="{node_id}" name="{node_name}" />\n'
        elif node_type == "exclusiveGateway":
            xml += f'    <bpmn:exclusiveGateway id="{node_id}" name="{node_name}" />\n'
        else:
            xml += f'    <!-- Tipo no reconocido: {node_type} -->\n'

    xml += "\n"

    # Agregar flujos
    for flow in data["process"]["flows"]:
        source = flow["source"]
        target = flow["target"]
        flow_id = flow["id"]
        condition = flow.get("condition")

        if condition:
            xml += f'''    <bpmn:sequenceFlow id="{flow_id}" sourceRef="{source}" targetRef="{target}">
      <bpmn:conditionExpression xsi:type="bpmn:tFormalExpression">{condition}</bpmn:conditionExpression>
    </bpmn:sequenceFlow>\n'''
        else:
            xml += f'    <bpmn:sequenceFlow id="{flow_id}" sourceRef="{source}" targetRef="{target}" />\n'

    xml += "  </bpmn:process>\n</bpmn:definitions>"
    return xml



#api_key=os.getenv("OPENAI_API_KEY")
os.environ['OPENROUTER_API_KEY'] = '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'
# Configurar el modelo con OpenRouter
llm = ChatOpenAI(
    model_name="meta-llama/llama-3-70b-instruct",
    openai_api_base="https://openrouter.ai/api/v1",
    openai_api_key=os.environ.get("OPENROUTER_API_KEY"),
    temperature=0.2
)

# Definir un prompt
prompt = PromptTemplate(
    input_variables=["user_input"],
    template="""
            Eres un experto en modelado de procesos. Recibirás una descripción en lenguaje natural y debes devolver una estructura JSON clara para generar un diagrama BPMN.

            Descripción del usuario:
            {user_input}

            Devuelve solo el JSON del proceso BPMN

    """
)

# Crear una cadena de LangChain
chain = LLMChain(llm=llm, prompt=prompt)

st.set_page_config(page_title="Generador BPMN con IA",layout="centered")
st.title("Generador de Procesos BPMN con IA")
descripcion=st.text_area("Describe tu proceso en lenguaje natural:")
if st.button("Generar JSON BPMN"):
    if descripcion.strip() == "":
        st.warning("Por favor escribe una descripción del proceso.")
    else:
        with st.spinner("Generando JSON..."):
            resultado = chain.run(user_input=descripcion)
            st.success("✅ Generado exitosamente:")
            st.code(resultado, language="json")
            """json_match = re.search(r'\{.*\}', resultado, re.DOTALL)

            if json_match:
                json_str = json_match.group(0)
                try:
                    parsed_json = json.loads(json_str)
                except json.JSONDecodeError as e:
                    st.error(f"❌ JSON inválido: {e}")
                    st.text(json_str)
                    st.stop()
            else:
                st.error("❌ No se pudo extraer JSON desde la respuesta del modelo.")
                st.text(resultado)
                st.stop()

            xml = json_to_bpmn_xml(parsed_json)
            with open("diagrama.bpmn", "w") as f:
                f.write(xml)
            st.components.v1.iframe("http://localhost:8501/visor.html", height=500)"""
# Ejecutar la cadena
#respuesta = chain.run(pregunta="¿Cual es la capital de la region del maule,chile?") 
#print(respuesta)
