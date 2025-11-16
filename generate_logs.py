"""
Script para generar logs abundantes y realistas para el dashboard ELK
CON AUTENTICACIÓN - Para API que requiere login
"""

import random
import time
import requests
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

# Configuración
API_BASE_URL = "http://localhost:8081/api"
NUM_REQUESTS = 200  

NOMBRE_USUARIO = os.getenv("NOMBRE_USUARIO") 
PASSWORD = os.getenv("PASSWORD")  

ENDPOINTS = [
    {"path": "/formularios-lite/", "method": "GET", "weight": 20},
    {"path": "/categorias/", "method": "GET", "weight": 15},
    {"path": "/dashboard/resumen/", "method": "GET", "weight": 10},
    {"path": "/usuarios/", "method": "GET", "weight": 8},
    {"path": "/asignaciones/", "method": "GET", "weight": 25},
    {"path": "/campos/", "method": "GET", "weight": 10},
    {"path": "/fuentes-datos/", "method": "GET", "weight": 7},
    {"path": "/grupos/", "method": "GET", "weight": 5},
]

ERROR_ENDPOINTS = [
    "/formularios/999999/",  # 404 - No existe
    "/formularios/abc/",      # 400 - ID inválido
    "/usuarios/999/",         # 404
    "/categorias/888/",       # 404
]


def login():
    """
    Realiza login y obtiene el token de autenticación
    """
    print("🔐 Autenticando con la API...")
    
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
            
            token = (
                data.get('access_token') or 
                data.get('token') or 
                data.get('access') or
                data.get('key')
            )
            
            if token:
                print(f"✅ Autenticación exitosa")
                return token
            else:
                print(f"❌ Token no encontrado en la respuesta: {data}")
                print("\n💡 Tip: Revisa qué campo contiene el token en la respuesta")
                return None
        else:
            print(f"❌ Error en login: {response.status_code}")
            print(f"Respuesta: {response.text}")
            return None
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Error de conexión en login: {str(e)}")
        return None


def generate_traffic(token):
    """
    Genera tráfico realista a la API usando el token de autenticación
    """
    if not token:
        print("❌ No se puede generar tráfico sin token")
        return
    
    print(f"\n🚀 Iniciando generación de {NUM_REQUESTS} requests...")
    print(f"📊 Esto generará logs estructurados para ELK\n")
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    success_count = 0
    error_count = 0
    
    for i in range(NUM_REQUESTS):
        # 90% requests normales, 10% requests con errores
        if random.random() < 0.9:
            endpoint = random.choices(
                ENDPOINTS,
                weights=[e["weight"] for e in ENDPOINTS]
            )[0]
            url = f"{API_BASE_URL}{endpoint['path']}"
            method = endpoint['method']
        else:
            error_path = random.choice(ERROR_ENDPOINTS)
            url = f"{API_BASE_URL}{error_path}"
            method = "GET"
        
        try:
            if method == "GET":
                response = requests.get(url, headers=headers, timeout=100)
            elif method == "POST":
                response = requests.post(url, json={}, headers=headers, timeout=100)
            
            if response.status_code < 400:
                success_count += 1
                status_icon = "✅"
            else:
                error_count += 1
                status_icon = "⚠️"
            
            # Log cada 50 requests
            if (i + 1) % 50 == 0:
                print(f"Progress: {i + 1}/{NUM_REQUESTS} requests "
                      f"(✅ {success_count} | ⚠️ {error_count})")
            
            # Simular comportamiento humano con delays variables
            delay = random.uniform(0.5, 1.5)
            time.sleep(delay)
            
        except requests.exceptions.RequestException as e:
            error_count += 1
            if (i + 1) % 50 == 0:
                print(f"❌ Error en request {i + 1}: {str(e)}")
    
    # Resumen final
    print("\n" + "="*60)
    print("📊 RESUMEN DE GENERACIÓN DE LOGS")
    print("="*60)
    print(f"✅ Requests exitosos: {success_count}")
    print(f"⚠️ Requests con errores: {error_count}")
    print(f"📝 Total de logs generados: {NUM_REQUESTS}")
    print(f"📁 Los logs están en: ./logs/api.log")
    print("\n🎯 Ahora puedes ver el dashboard en Kibana:")
    print("   http://localhost:5601")
    print("="*60)


def generate_burst_traffic(token):
    """
    Genera ráfagas de tráfico para simular picos de uso
    """
    if not token:
        return
    
    print("\n🔥 Generando ráfaga de tráfico intenso...")
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    for burst in range(3):
        print(f"\n💥 Ráfaga {burst + 1}/3")
        for i in range(50):
            endpoint = random.choice(ENDPOINTS)
            url = f"{API_BASE_URL}{endpoint['path']}"
            
            try:
                requests.get(url, headers=headers, timeout=2)
                if (i + 1) % 10 == 0:
                    print(f"  → {i + 1}/50 requests enviados")
            except:
                pass
            
            # Delay muy corto para simular tráfico intenso
            time.sleep(0.05)
        
        # Pausa entre ráfagas
        if burst < 2:
            print("  ⏸️ Pausa de 2 segundos...")
            time.sleep(2)


if __name__ == "__main__":
    print("="*60)
    print("🎯 GENERADOR DE LOGS PARA ELK DASHBOARD")
    print("   Santa Ana AgroForms API (CON AUTENTICACIÓN)")
    print("="*60)
    print("\nAsegúrate de que:")
    print(f"  1. La API esté corriendo en: {API_BASE_URL}")
    print(f"  2. Usuario: {NOMBRE_USUARIO}")
    print(f"  3. Password configurado correctamente\n")
    
    # Paso 1: Autenticar
    token = login()
    
    if not token:
        print("\n❌ No se pudo obtener el token de autenticación")
        print("\n💡 Verifica:")
        print("   - Que la API esté corriendo: docker-compose ps")
        print("   - Que el usuario y password sean correctos")
        print("   - La URL del login: http://127.0.0.1:8081/api/auth/login/")
        exit(1)
    
    # Paso 2: Generar tráfico
    input("\n✅ Token obtenido. Presiona ENTER para comenzar...")
    generate_traffic(token)
    
    # Paso 3 (Opcional): Ráfagas
    print("\n¿Quieres generar ráfagas adicionales de tráfico? (s/n)")
    if input().lower() == 's':
        generate_burst_traffic(token)
    
    print("\n✨ ¡Listo! Revisa Kibana para ver tus logs.")
    print("🌐 http://localhost:5601")