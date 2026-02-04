import requests
import json
import time

# CONFIGURACIÓN
CRM_URL = "http://127.0.0.1:5000/tickets"
API_KEY = "TKN-3D9A855B"

def test_integration():
    print("🔌 PROBANDO INTEGRACIÓN CON OFICINA CENTRAL (MOCK)...")
    
    # Datos simulados de ChechyLegis
    ticket = {
        "subject": "Error Crítico: Núcleo Penal inestable",
        "description": "Se detectó una inconsistencia en el análisis de tipicidad durante la prueba de carga.",
        "priority": "high",
        "user_email": "tester@gahenax.com",
        "metadata": {
            "version": "1.1.0",
            "module": "penal_core"
        }
    }
    
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    
    try:
        # Intentar enviar
        print(f"📨 Enviando ticket a {CRM_URL}...")
        response = requests.post(CRM_URL, json=ticket, headers=headers, timeout=5)
        
        # Verificar respuesta
        if response.status_code == 201:
            data = response.json()
            print("\n✅ ÉXITO TOTAL")
            print(f"🆔 Ticket ID: {data['id']}")
            print(f"🏢 Firma Oficina: {data['office_signature']}")
            print("📝 Mensaje: Ticket registrado invisiblemente.")
            return True
        else:
            print(f"\n❌ FALLO EL ENVÍO: {response.status_code}")
            print(response.text)
            return False
            
    except requests.exceptions.ConnectionError:
        print("\n❌ FALLO DE CONEXIÓN")
        print("El servidor King CRM (Mock) no parece estar corriendo en el puerto 5000.")
        return False
    except Exception as e:
        print(f"\n❌ ERROR INESPERADO: {e}")
        return False

if __name__ == "__main__":
    # Esperar un momento para asegurar que el server levantó
    time.sleep(2)
    test_integration()
