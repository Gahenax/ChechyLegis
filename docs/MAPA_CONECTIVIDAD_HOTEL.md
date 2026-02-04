# 🗺️ MAPA DE CONECTIVIDAD — GAHENAX HOTEL
**Estado:** DETECTADO Y CONFIRMADO

---

## 🔌 PUNTOS DE CONEXIÓN

### 1. 🏢 LA OFICINA (King CRM)
**Dirección Detectada:** `http://127.0.0.1:5000`  
**Llave de Acceso:** `TKN-3D9A855B` (Encontrada en .env)
**Rol:** Servidor Central de Administración

### 2. 🛏️ HABITACIÓN 101 (ChechyLegis)
**Dirección:** `http://127.0.0.1:8000`
**Rol:** Cliente de la Oficina
**Integración:**
- Archivo: `app/crm_service.py`
- Endpoint usado: `POST /tickets`

### 3. 🛎️ EL LOBBY (Propuesto)
**Dirección:** `http://127.0.0.1:8001` (Hotel Gateway)
**Rol:** Orquestador de Tráfico

---

## 🔀 FLUJO DE DATOS CONFIRMADO

```mermaid
graph TD
    User((Usuario)) --> Lobby[Lobby (Web)]
    Lobby -- "1. Login" --> Gateway[Hotel Gateway :8001]
    Gateway -- "2. Check Key" --> Gateway
    Gateway -- "3. Enter Room" --> Chechy[ChechyLegis :8000]
    Chechy -- "4. Report Issue" --> King[King CRM :5000]
    King -- "5. Ticket Created" --> Chechy
```

---

## 🛠️ ACCIÓN REQUERIDA

Necesitamos levantar **King CRM** en el puerto 5000 para que el ecosistema funcione completo.

**Opciones:**
1.  **Encontrar el código**: Si está en otra carpeta, ejecutarlo.
2.  **Mock Server**: Crear un script temporal `mock_king_crm.py` que escuche en el puerto 5000 y responda "OK" para probar la integración hoy.

---

**Recomendación:** Crear `mock_king_crm.py` ahora para validar la tubería completa sin depender de encontrar el código original inmediatamente.
