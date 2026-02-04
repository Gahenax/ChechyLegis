import os
import sys
import time
from pyngrok import ngrok, conf
import subprocess
import threading
from dotenv import load_dotenv

load_dotenv()

def start_server():
    """Starts the uvicorn server in a separate thread"""
    # Use standard uvicorn command
    cmd = [sys.executable, "-m", "uvicorn", "app.main:app", "--host", "127.0.0.1", "--port", "8000"]
    subprocess.run(cmd)

def main():
    # Force UTF-8 output for Windows terminals
    if sys.platform == "win32":
        sys.stdout.reconfigure(encoding='utf-8')
    
    print("🚀 Configurando servidor público con Ngrok...")
    
    # Check for authtoken
    token = os.getenv("NGROK_AUTHTOKEN")
    if not token:
        print("\n⚠️  ADVERTENCIA: No se encontró NGROK_AUTHTOKEN en las variables de entorno.")
        print("   Para que la web sea accesible públicamente, Ngrok requiere un token.")
        print("   Puedes obtener uno gratis en: https://dashboard.ngrok.com/get-started/your-authtoken")
        print("   Tip: Agrega NGROK_AUTHTOKEN=tu_token en el archivo .env")
        
        token_input = input("\n   Ingresa tu NGROK AUTHTOKEN (o presiona Enter para intentar sin uno): ").strip()
        if token_input:
            token = token_input
    
    if token:
        try:
            ngrok.set_auth_token(token)
            print("✅ Authtoken configurado.")
        except Exception as e:
            print(f"⚠️ Error configurando token: {e}")

    # Start the local server if not running
    print("📦 Iniciando servidor local (Uvicorn)...")
    server_thread = threading.Thread(target=start_server, daemon=True)
    server_thread.start()
    
    # Give it a moment to start
    time.sleep(3)

    try:
        # Open the tunnel
        # http_tunnel = ngrok.connect(8000, "http") 
        # Note: newer pyngrok uses connect(addr, proto) or just port
        public_url = ngrok.connect(8000).public_url
        
        print("\n" + "="*60)
        print(f"🎉 JULES DICE: TU APP ESTÁ EN VIVO EN LA NUBE!")
        print("="*60)
        print(f"🌍 URL Pública: {public_url}")
        print(f"🏠 Local URL:   http://127.0.0.1:8000")
        print("="*60)
        print("\nPresiona Ctrl+C para detener el servidor y cerrar el túnel.")
        
        # Keep the script running
        ngrok_process = ngrok.get_ngrok_process()
        ngrok_process.proc.wait()
    except KeyboardInterrupt:
        print("\n🛑 Deteniendo servidor...")
        ngrok.kill()
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error al iniciar Ngrok: {e}")
        print("   Verifica que no tengas otro proceso de Ngrok corriendo o que tu token sea válido.")

if __name__ == "__main__":
    main()
