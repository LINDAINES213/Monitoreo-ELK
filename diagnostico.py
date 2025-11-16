"""
Script de DIAGNÓSTICO COMPLETO
Primero verifica el formato del token, luego genera logs
"""

import requests
import json

# Configuración - EDITA ESTOS VALORES
API_BASE_URL = "http://localhost:8081/api"
NOMBRE_USUARIO = "admin"  # ← Cambia esto
PASSWORD = "Admin123"   # ← Cambia esto

print("="*70)
print("🔍 INVESTIGANDO ERROR 500 CON BEARER TOKEN")
print("="*70)

# Paso 1: Login
print("\n1️⃣ Haciendo LOGIN...\n")

try:
    response = requests.post(
        f"{API_BASE_URL}/auth/login/",
        json={
            "nombre_usuario": NOMBRE_USUARIO,
            "password": PASSWORD
        },
        timeout=10
    )
    
    if response.status_code == 200:
        data = response.json()
        token = data['access_token']
        print(f"✅ Token obtenido: {token[:30]}...")
        print(f"📝 Tipo: {data['token_type']}")
        print(f"⏱️ Expira en: {data['expires_in']} segundos")
    else:
        print(f"❌ Login falló")
        exit(1)
        
except Exception as e:
    print(f"❌ Error: {e}")
    exit(1)

# Paso 2: INMEDIATAMENTE probar con Bearer (antes de que expire)
print("\n2️⃣ Probando INMEDIATAMENTE con Bearer token...\n")

headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json",
    "Accept": "application/json"
}

test_url = f"{API_BASE_URL}/auth/me/"

print(f"🌐 URL: {test_url}")
print(f"📋 Headers: {headers}")

try:
    response = requests.get(test_url, headers=headers, timeout=10)
    
    print(f"\n📊 Status Code: {response.status_code}")
    print(f"📋 Response Headers: {dict(response.headers)}")
    
    if response.status_code == 200:
        print(f"\n✅ ¡FUNCIONA!")
        print(f"Respuesta: {response.json()}")
    elif response.status_code == 500:
        print(f"\n❌ ERROR 500 - Error del Servidor")
        print(f"\n📄 Contenido completo de la respuesta:")
        print(response.text)
        
        print(f"\n💡 POSIBLES CAUSAS DEL ERROR 500:")
        print("1. El servidor tiene DEBUG=False y no muestra el error")
        print("2. Hay un problema con OAuth2Provider en el servidor")
        print("3. El token es válido pero hay un bug en la validación")
        
        print(f"\n🔍 PRÓXIMOS PASOS:")
        print("1. Revisa los logs del servidor ahora:")
        print("   docker-compose logs api --tail=20")
        print("\n2. O activa DEBUG en settings.py temporalmente")
        
    else:
        print(f"\n❌ Código: {response.status_code}")
        print(f"Respuesta: {response.text}")
        
except Exception as e:
    print(f"❌ Error en request: {e}")

# Paso 3: Probar otros endpoints también
print("\n" + "="*70)
print("3️⃣ Probando otros endpoints con Bearer token")
print("="*70)

endpoints = [
    "/formularios/",
    "/categorias/",
    "/dashboard/resumen/"
]

for endpoint in endpoints:
    try:
        response = requests.get(
            f"{API_BASE_URL}{endpoint}",
            headers=headers,
            timeout=100
        )
        status_icon = "✅" if response.status_code < 400 else "❌"
        print(f"{status_icon} {endpoint}: {response.status_code}")
        
        if response.status_code == 500:
            print(f"   ⚠️ Error 500 - ver detalles en logs del servidor")
            
    except Exception as e:
        print(f"❌ {endpoint}: {e}")

print("\n" + "="*70)
print("📋 RESUMEN")
print("="*70)
print("\n🔍 Si ves error 500, revisa los logs del servidor:")
print("   docker-compose logs api --tail=50 --follow")
print("\n💡 Busca líneas con 'ERROR' o 'Traceback'")
print("="*70)












