"""
Script para generar logs abundantes y realistas para el dashboard ELK
CON MÚLTIPLES USUARIOS - Simula actividad de varios usuarios diferentes
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
NUM_REQUESTS = 35  

# ==========================================
# MÚLTIPLES USUARIOS - Define aquí tus usuarios
# ==========================================
USUARIOS = [
    {
        "nombre_usuario": os.getenv("NOMBRE_USUARIO"),
        "password": os.getenv("PASSWORD"),
        "peso": 40,  # 40% de las peticiones
        "token": None
    },
    {
        "nombre_usuario": os.getenv("NOMBRE_USUARIO2"),
        "password": os.getenv("PASSWORD2"),
        "peso": 30,  # 30% de las peticiones
        "token": None
    },
    {
        "nombre_usuario": os.getenv("NOMBRE_USUARIO3"),
        "password": os.getenv("PASSWORD3"),
        "peso": 30,  
        "token": None
    },
]

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
    "/formularios/999999/",
    "/formularios/abc/",
    "/usuarios/999/",
    "/categorias/888/",
]

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


def login_all_users():
    """
    Realiza login para todos los usuarios y obtiene sus tokens
    """
    print("🔐 Autenticando todos los usuarios...\n")
    
    successful_logins = 0
    
    for usuario in USUARIOS:
        print(f"   Autenticando: {usuario['nombre_usuario']}...", end=" ")
        
        try:
            response = requests.post(
                f"{API_BASE_URL}/auth/login/",
                json={
                    "nombre_usuario": usuario['nombre_usuario'],
                    "password": usuario['password']
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
                    usuario['token'] = token
                    print(f"✅")
                    successful_logins += 1
                else:
                    print(f"❌ (Token no encontrado)")
            else:
                print(f"❌ (Status: {response.status_code})")
                
        except requests.exceptions.RequestException as e:
            print(f"❌ (Error: {str(e)})")
    
    print(f"\n✅ {successful_logins}/{len(USUARIOS)} usuarios autenticados exitosamente\n")
    
    return successful_logins > 0


def get_random_user():
    """
    Selecciona un usuario aleatorio basado en los pesos
    """
    usuarios_con_token = [u for u in USUARIOS if u['token']]
    
    if not usuarios_con_token:
        return None
    
    return random.choices(
        usuarios_con_token,
        weights=[u['peso'] for u in usuarios_con_token]
    )[0]


def create_categoria(usuario, nombre):
    """
    Crea una categoría usando el token del usuario especificado
    """
    headers = {
        "Authorization": f"Bearer {usuario['token']}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "nombre": nombre,
        "descripcion": f"Creada por {usuario['nombre_usuario']} - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
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
            print(f"   ✅ [{usuario['nombre_usuario']}] Categoría creada: '{nombre}' (ID: {categoria_id})")
            return categoria_id
        else:
            print(f"   ⚠️ [{usuario['nombre_usuario']}] Error creando: {response.status_code}")
            return None
            
    except requests.exceptions.RequestException as e:
        print(f"   ❌ [{usuario['nombre_usuario']}] Error en POST: {str(e)}")
        return None


def delete_categoria(usuario, categoria_id):
    """
    Elimina una categoría usando el token del usuario especificado
    """
    headers = {
        "Authorization": f"Bearer {usuario['token']}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.delete(
            f"{API_BASE_URL}/categorias/{categoria_id}/",
            headers=headers,
            timeout=10
        )
        
        if response.status_code in [200, 204]:
            print(f"   🗑️ [{usuario['nombre_usuario']}] Categoría eliminada (ID: {categoria_id})")
            return True
        else:
            print(f"   ⚠️ [{usuario['nombre_usuario']}] Error eliminando: {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"   ❌ [{usuario['nombre_usuario']}] Error en DELETE: {str(e)}")
        return False


def generate_crud_logs(num_categorias=10):
    """
    Genera logs de CRUD con DIFERENTES USUARIOS
    """
    print(f"\n📝 Generando logs de CRUD con múltiples usuarios...")
    print(f"   Crearemos y eliminaremos {num_categorias} categorías\n")
    
    created_items = []  # Lista de tuplas (categoria_id, usuario)
    
    # Fase 1: Crear categorías con diferentes usuarios
    print("🆕 FASE 1: Creando categorías (usuarios alternados)...")
    for i in range(num_categorias):
        usuario = get_random_user()
        
        if not usuario:
            print("   ❌ No hay usuarios disponibles")
            break
        
        nombre = f"{random.choice(CATEGORIA_NOMBRES)} {i+1}"
        categoria_id = create_categoria(usuario, nombre)
        
        if categoria_id:
            created_items.append((categoria_id, usuario))
        
        time.sleep(random.uniform(1, 2))
    
    print(f"\n✅ {len(created_items)} categorías creadas por diferentes usuarios")
    
    # Resumen de quién creó qué
    user_stats = {}
    for _, usuario in created_items:
        username = usuario['nombre_usuario']
        user_stats[username] = user_stats.get(username, 0) + 1
    
    print("\n📊 Resumen de creaciones por usuario:")
    for username, count in user_stats.items():
        print(f"   - {username}: {count} categorías")
    
    # Pausa
    print("\n⏸️ Pausa de 3 segundos antes de eliminar...")
    time.sleep(3)
    
    # Fase 2: Eliminar categorías (pueden ser eliminadas por usuarios diferentes)
    print("\n🗑️ FASE 2: Eliminando categorías (usuarios alternados)...")
    deleted_count = 0
    
    for categoria_id, _ in created_items:
        # Elegir usuario aleatorio para eliminar (no necesariamente el creador)
        usuario = get_random_user()
        
        if usuario and delete_categoria(usuario, categoria_id):
            deleted_count += 1
        
        time.sleep(random.uniform(1, 2))
    
    print(f"\n✅ {deleted_count} categorías eliminadas")
    
    return len(created_items), deleted_count


def generate_traffic():
    """
    Genera tráfico realista con MÚLTIPLES USUARIOS
    """
    print(f"\n🚀 Iniciando generación de {NUM_REQUESTS} requests con usuarios variados...\n")
    
    success_count = 0
    error_count = 0
    user_request_count = {u['nombre_usuario']: 0 for u in USUARIOS if u['token']}
    
    for i in range(NUM_REQUESTS):
        # Seleccionar usuario aleatorio
        usuario = get_random_user()
        
        if not usuario:
            print("   ❌ No hay usuarios disponibles")
            break
        
        user_request_count[usuario['nombre_usuario']] += 1
        
        headers = {
            "Authorization": f"Bearer {usuario['token']}",
            "Content-Type": "application/json"
        }
        
        # 90% requests normales, 10% con errores
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
            
            # Log cada 20 requests
            if (i + 1) % 20 == 0:
                print(f"Progress: {i + 1}/{NUM_REQUESTS} requests "
                      f"(✅ {success_count} | ⚠️ {error_count})")
            
            # Delay variable
            delay = random.uniform(0.3, 1.5)
            time.sleep(delay)
            
        except requests.exceptions.RequestException as e:
            error_count += 1
    
    # Resumen final
    print("\n" + "="*60)
    print("📊 RESUMEN DE GENERACIÓN DE LOGS")
    print("="*60)
    print(f"✅ Requests exitosos: {success_count}")
    print(f"⚠️ Requests con errores: {error_count}")
    print(f"📝 Total de logs: {NUM_REQUESTS}")
    print("\n📊 Distribución por usuario:")
    for username, count in sorted(user_request_count.items(), key=lambda x: x[1], reverse=True):
        percentage = (count / NUM_REQUESTS) * 100
        print(f"   - {username}: {count} requests ({percentage:.1f}%)")
    print("="*60)


if __name__ == "__main__":
    print("="*60)
    print("🎯 GENERADOR DE LOGS PARA ELK DASHBOARD")
    print("   Santa Ana AgroForms API (MULTI-USUARIO)")
    print("="*60)
    print(f"\nAPI: {API_BASE_URL}")
    print(f"\nUsuarios configurados: {len(USUARIOS)}")
    for u in USUARIOS:
        print(f"   - {u['nombre_usuario']} (peso: {u['peso']}%)")
    print()
    
    # Autenticar todos los usuarios
    if not login_all_users():
        print("\n❌ No se pudo autenticar ningún usuario")
        print("\n💡 Verifica:")
        print("   - Que la API esté corriendo")
        print("   - Que los usuarios existan en la base de datos")
        print("   - Que las contraseñas sean correctas")
        exit(1)
    
    print("\n¿Qué operación deseas realizar?")
    print("1. Solo CRUD de categorías (usuarios alternados)")
    print("2. Solo tráfico GET normal (usuarios variados)")
    print("3. Ambos (CRUD + tráfico)")
    
    opcion = input("\nElige una opción (1/2/3): ").strip()
    
    if opcion == "1":
        num_cat = input("\n¿Cuántas categorías crear/eliminar? (default: 10): ").strip()
        num_cat = int(num_cat) if num_cat else 10
        generate_crud_logs(num_cat)
        
    elif opcion == "2":
        generate_traffic()
        
    elif opcion == "3":
        print("\n🔄 PARTE 1: CRUD de categorías")
        num_cat = input("¿Cuántas categorías crear/eliminar? (default: 10): ").strip()
        num_cat = int(num_cat) if num_cat else 10
        generate_crud_logs(num_cat)
        
        print("\n🔄 PARTE 2: Tráfico normal")
        input("Presiona ENTER para continuar...")
        generate_traffic()
    
    else:
        print("❌ Opción inválida")
        exit(1)
    
    print("\n✨ ¡Listo! Revisa Kibana para ver logs de múltiples usuarios.")
    print("💡 Ahora puedes crear visualizaciones como 'Top Usuarios Más Activos'")