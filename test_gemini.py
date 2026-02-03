"""
Script de prueba para verificar la integración con Gemini API
Ejecutar: python test_gemini.py
"""

import os
from dotenv import load_dotenv
from app.gemini_service import GeminiService

# Cargar variables de entorno
load_dotenv()

def test_gemini_connection():
    """Prueba la conexión con Gemini API"""
    
    print("🔍 Verificando configuración de Gemini API...\n")
    
    # Verificar API key
    api_key = os.getenv("GEMINI_API_KEY")
    
    if not api_key or api_key == "tu_api_key_aqui":
        print("❌ ERROR: API Key de Gemini no configurada")
        print("📝 Por favor:")
        print("   1. Edita el archivo .env")
        print("   2. Reemplaza 'tu_api_key_aqui' con tu API key real")
        print("   3. Obtén tu API key en: https://aistudio.google.com/app/apikey")
        return False
    
    print(f"✅ API Key encontrada: {api_key[:10]}...{api_key[-5:]}")
    
    # Inicializar servicio
    try:
        print("\n🤖 Inicializando servicio de Gemini...")
        service = GeminiService(api_key)
        print("✅ Servicio inicializado correctamente")
    except Exception as e:
        print(f"❌ Error al inicializar servicio: {e}")
        return False
    
    # Prueba 1: Chat Assistant
    print("\n📝 Prueba 1: Asistente Conversacional")
    try:
        response = service.chat_assistant("¿Qué es un proceso judicial?")
        print(f"✅ Respuesta recibida ({len(response)} caracteres)")
        print(f"📄 Respuesta: {response[:200]}...")
    except Exception as e:
        print(f"❌ Error en chat: {e}")
        return False
    
    # Prueba 2: Parse Natural Query
    print("\n📝 Prueba 2: Búsqueda en Lenguaje Natural")
    try:
        result = service.parse_natural_query("procesos activos de enero", [])
        print(f"✅ Consulta interpretada correctamente")
        print(f"📄 Interpretación: {result.get('interpretacion', 'N/A')}")
        print(f"📄 Filtros: {result.get('filtros', {})}")
    except Exception as e:
        print(f"❌ Error en búsqueda natural: {e}")
        return False
    
    # Prueba 3: Analyze Proceso
    print("\n📝 Prueba 3: Análisis de Proceso")
    proceso_ejemplo = {
        "numero_proceso": "2024-001",
        "estado": "ACTIVO",
        "fecha_radicacion": "2024-01-15",
        "partes": "Juan Pérez vs María García",
        "clase_proceso": "Civil",
        "cuantia_tipo": "MAYOR",
        "observaciones": "Proceso de divorcio contencioso"
    }
    
    try:
        analysis = service.analyze_proceso(proceso_ejemplo)
        print(f"✅ Análisis generado correctamente")
        print(f"📄 Resumen: {analysis.get('resumen', 'N/A')}")
        print(f"📄 Alertas: {len(analysis.get('alertas', []))} alertas encontradas")
    except Exception as e:
        print(f"❌ Error en análisis: {e}")
        return False
    
    print("\n" + "="*60)
    print("🎉 ¡TODAS LAS PRUEBAS PASARON EXITOSAMENTE!")
    print("="*60)
    print("\n✅ El sistema está listo para usar con Gemini AI")
    print("🚀 Inicia el servidor con: uvicorn app.main:app --reload --port 8000")
    print("🌐 Luego abre: http://127.0.0.1:8000")
    
    return True

if __name__ == "__main__":
    try:
        test_gemini_connection()
    except KeyboardInterrupt:
        print("\n\n⚠️  Prueba interrumpida por el usuario")
    except Exception as e:
        print(f"\n\n❌ Error inesperado: {e}")
        import traceback
        traceback.print_exc()
