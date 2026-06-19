import os
import google.generativeai as genai
from django.conf import settings
import json

api_key = getattr(settings, 'GEMINI_API_KEY', os.environ.get('GEMINI_API_KEY'))

if api_key:
    genai.configure(api_key=api_key)

def analizar_documento_rendicion(file_path):
    """
    Sube un archivo a Gemini y le pide que extraiga el monto y observaciones.
    """
    if not api_key:
        return {"monto": 0, "observaciones": "API Key de Gemini no configurada."}

    try:
        # Subir archivo a la API de Gemini (soporta PDF, JPEG, PNG, etc.)
        sample_file = genai.upload_file(path=file_path)
        
        model = genai.GenerativeModel(model_name="gemini-1.5-flash")
        
        prompt = (
            "Analiza el siguiente documento de rendición de gastos (puede ser boleta, factura, "
            "liquidación de sueldo, comprobante, etc.). Extrae el monto financiero TOTAL o más "
            "importante que deba rendirse (sólo números enteros sin puntos ni signos), y cualquier observación relevante (máximo 1 oración).\n"
            "Devuelve ÚNICAMENTE un JSON válido con este formato exacto, sin bloques de código markdown ni texto adicional:\n"
            '{"monto": 150000, "observaciones": "Pago de servicios"}'
        )
        
        response = model.generate_content([sample_file, prompt])
        
        # Limpiar la respuesta para parsear el JSON
        text = response.text.strip()
        if text.startswith('```json'):
            text = text[7:]
        if text.startswith('```'):
            text = text[3:]
        if text.endswith('```'):
            text = text[:-3]
            
        data = json.loads(text.strip())
        
        # Opcional: borrar el archivo de Gemini después de usarlo para ahorrar cuota
        genai.delete_file(sample_file.name)
        
        return {
            "monto": int(data.get("monto", 0)),
            "observaciones": data.get("observaciones", "Sin observaciones adicionales")
        }
    except Exception as e:
        print(f"Error analizando con Gemini: {e}")
        return {"monto": 0, "observaciones": f"Error al analizar el documento."}
