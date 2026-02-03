"""
Convierte el icono PNG a formato ICO para Windows
"""

try:
    from PIL import Image
    import sys
    
    print("Convirtiendo icon.png a icon.ico...")
    
    # Abrir la imagen PNG
    img = Image.open('icon.png')
    
    # Convertir a ICO con múltiples tamaños
    img.save('icon.ico', format='ICO', sizes=[(16,16), (32,32), (48,48), (64,64), (128,128), (256,256)])
    
    print("OK: Conversion exitosa!")
    print("   Archivo creado: icon.ico")
    print()
    print("Ahora puedes:")
    print("1. Ejecutar: crear_acceso_directo.ps1")
    print("2. O manualmente: Clic derecho en el acceso directo > Propiedades > Cambiar icono")
    
except ImportError:
    print("ADVERTENCIA: Pillow no esta instalado")
    print("   Instalando Pillow...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "Pillow"])
    print("OK: Pillow instalado. Ejecuta este script nuevamente.")
except Exception as e:
    print(f"ERROR: {e}")

input("\nPresiona Enter para continuar...")
