# Script para subir ChechyLegis a GitHub
# Ejecuta estos comandos en orden

# 1. Configurar Git (REEMPLAZA con tu información)
git config --global user.name "Tu Nombre"
git config --global user.email "tu_email@example.com"

# 2. Hacer el commit inicial
git commit -m "Initial commit: Archivo Virtual de Procesos Judiciales con IA (Gemini)"

# 3. Crear el repositorio en GitHub
# Ve a: https://github.com/new
# Nombre del repositorio: ChechyLegis
# Descripción: Archivo Virtual de Procesos Judiciales con IA (Gemini)
# Público o Privado: Tu elección
# NO inicialices con README, .gitignore, o licencia (ya los tenemos)

# 4. Conectar con GitHub (REEMPLAZA con tu usuario)
git remote add origin https://github.com/TU_USUARIO/ChechyLegis.git

# 5. Cambiar a rama main (si es necesario)
git branch -M main

# 6. Subir el código
git push -u origin main

# NOTA: Si GitHub pide autenticación, usa un Personal Access Token
# Créalo en: https://github.com/settings/tokens
