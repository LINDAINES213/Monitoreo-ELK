"""
Script para generar logs abundantes y realistas para el dashboard ELK
CON AUTENTICACIÓN - Incluye POST y DELETE de categorías
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
NUM_REQUESTS = 100  

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

# Nombres para categorías de prueba
CATEGORIA_NOMBRES = [
    "Prueba ELK Dashboard",
    "Categoría Temporal",
    "Test Monitoreo",
    "Logs ELK Test",
    "Dashboard Demo",
    "Categoría de Prueba",
    "Monitoreo Temporal",
    "Test Logging",
    "ELK Stack Test",
    "Demo Category",
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


def create_categoria(token, nombre):
    """
    Crea una categoría y retorna su ID
    """
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # Ajusta este payload según tu modelo de Categoría
    payload = {
        "nombre": nombre,
        "descripcion": f"Categoría creada para pruebas de logging - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        # Agrega otros campos requeridos por tu modelo aquí
    }
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/categorias/",
            json=payload,
            headers=headers,
            timeout=10
        )
        
        if response.status_code in [200, 201]:
            data = response.json()
            categoria_id = data.get('id') or data.get('pk')
            print(f"   ✅ Categoría creada: '{nombre}' (ID: {categoria_id})")
            return categoria_id
        else:
            print(f"   ⚠️ Error creando categoría: {response.status_code}")
            return None
            
    except requests.exceptions.RequestException as e:
        print(f"   ❌ Error en POST: {str(e)}")
        return None


def delete_categoria(token, categoria_id):
    """
    Elimina una categoría por su ID
    """
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.delete(
            f"{API_BASE_URL}/categorias/{categoria_id}/",
            headers=headers,
            timeout=10
        )
        
        if response.status_code in [200, 204]:
            print(f"   🗑️ Categoría eliminada (ID: {categoria_id})")
            return True
        else:
            print(f"   ⚠️ Error eliminando categoría: {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"   ❌ Error en DELETE: {str(e)}")
        return False


def generate_crud_logs(token, num_categorias=10):
    """
    Genera logs de CRUD (Create y Delete) de categorías
    """
    print(f"\n📝 Generando logs de CRUD de categorías...")
    print(f"   Crearemos y eliminaremos {num_categorias} categorías\n")
    
    created_ids = []
    
    # Fase 1: Crear categorías
    print("🆕 FASE 1: Creando categorías...")
    for i in range(num_categorias):
        nombre = f"{random.choice(CATEGORIA_NOMBRES)} {i+1}"
        categoria_id = create_categoria(token, nombre)
        
        if categoria_id:
            created_ids.append(categoria_id)
        
        # Delay entre creaciones
        time.sleep(random.uniform(1, 2))
    
    print(f"\n✅ {len(created_ids)} categorías creadas exitosamente")
    
    # Pausa entre fases
    print("\n⏸️ Pausa de 3 segundos antes de eliminar...")
    time.sleep(3)
    
    # Fase 2: Eliminar categorías
    print("\n🗑️ FASE 2: Eliminando categorías...")
    deleted_count = 0
    
    for categoria_id in created_ids:
        if delete_categoria(token, categoria_id):
            deleted_count += 1
        
        # Delay entre eliminaciones
        time.sleep(random.uniform(1, 2))
    
    print(f"\n✅ {deleted_count} categorías eliminadas exitosamente")
    
    return len(created_ids), deleted_count


def generate_traffic(token):
    """
    Genera tráfico realista a la API usando el token de autenticación
    """
    if not token:
        print("❌ No se puede generar tráfico sin token")
        return
    
    print(f"\n🚀 Iniciando generación de {NUM_REQUESTS} requests...\n")
    
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
                response = requests.get(url, headers=headers, timeout=10)
            elif method == "POST":
                response = requests.post(url, json={}, headers=headers, timeout=10)
            
            if response.status_code < 400:
                success_count += 1
            else:
                error_count += 1
            
            # Log cada 50 requests
            if (i + 1) % 50 == 0:
                print(f"Progress: {i + 1}/{NUM_REQUESTS} requests "
                      f"(✅ {success_count} | ⚠️ {error_count})")
            
            # Simular comportamiento humano con delays variables
            delay = random.uniform(0.3, 1.0)
            time.sleep(delay)
            
        except requests.exceptions.RequestException as e:
            error_count += 1
    
    # Resumen final
    print("\n" + "="*60)
    print("📊 RESUMEN DE GENERACIÓN DE LOGS")
    print("="*60)
    print(f"✅ Requests exitosos: {success_count}")
    print(f"⚠️ Requests con errores: {error_count}")
    print(f"📝 Total de logs generados: {NUM_REQUESTS}")
    print("="*60)


if __name__ == "__main__":
    print("="*60)
    print("🎯 GENERADOR DE LOGS PARA ELK DASHBOARD")
    print("   Santa Ana AgroForms API (CON CRUD)")
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
        print("   - La URL del login")
        exit(1)
    
    print("\n¿Qué operación deseas realizar?")
    print("1. Solo CRUD de categorías (crear + eliminar)")
    print("2. Solo tráfico GET normal")
    print("3. Ambos (CRUD + tráfico GET)")
    
    opcion = input("\nElige una opción (1/2/3): ").strip()
    
    if opcion == "1":
        # Solo CRUD
        num_cat = input("\n¿Cuántas categorías crear/eliminar? (default: 10): ").strip()
        num_cat = int(num_cat) if num_cat else 10
        generate_crud_logs(token, num_cat)
        
    elif opcion == "2":
        # Solo tráfico normal
        generate_traffic(token)
        
    elif opcion == "3":
        # Primero CRUD
        print("\n🔄 PARTE 1: CRUD de categorías")
        num_cat = input("¿Cuántas categorías crear/eliminar? (default: 10): ").strip()
        num_cat = int(num_cat) if num_cat else 10
        generate_crud_logs(token, num_cat)
        
        # Luego tráfico normal
        print("\n🔄 PARTE 2: Tráfico normal")
        input("Presiona ENTER para continuar...")
        generate_traffic(token)
    
    else:
        print("❌ Opción inválida")
        exit(1)
    
    print("\n✨ ¡Listo! Revisa Kibana para ver tus logs.")
    print("🌐 Kibana Cloud: https://tu-endpoint.kb.us-east-1.aws.found.io:9243")