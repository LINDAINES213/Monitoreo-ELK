"""
Script de verificación para el sistema ELK
Verifica que todos los componentes estén funcionando correctamente
"""

import requests
import time
import sys
from pathlib import Path

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'
    BOLD = '\033[1m'

def print_header(text):
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{text:^60}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.END}\n")

def print_success(text):
    print(f"{Colors.GREEN}✓{Colors.END} {text}")

def print_error(text):
    print(f"{Colors.RED}✗{Colors.END} {text}")

def print_warning(text):
    print(f"{Colors.YELLOW}⚠{Colors.END} {text}")

def print_info(text):
    print(f"{Colors.BLUE}ℹ{Colors.END} {text}")

def check_service(name, url, expected_status=200):
    """Verifica si un servicio está disponible"""
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == expected_status:
            print_success(f"{name} está corriendo ({url})")
            return True
        else:
            print_warning(f"{name} respondió con código {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print_error(f"{name} no está disponible ({url})")
        return False
    except Exception as e:
        print_error(f"{name} - Error: {str(e)}")
        return False

def check_elasticsearch_indices():
    """Verifica que existan índices en Elasticsearch"""
    try:
        response = requests.get("http://localhost:9200/_cat/indices?v", timeout=5)
        if response.status_code == 200:
            indices = response.text
            if "santa-ana" in indices:
                print_success("Índices de logs encontrados en Elasticsearch")
                print_info("Índices disponibles:")
                for line in indices.split('\n'):
                    if 'santa-ana' in line:
                        print(f"  → {line}")
                return True
            else:
                print_warning("No se encontraron índices de logs (aún no hay datos)")
                return False
    except Exception as e:
        print_error(f"Error al verificar índices: {str(e)}")
        return False

def check_log_file():
    """Verifica que exista el archivo de logs y tenga contenido"""
    log_file = Path("logs/api.log")
    
    if not log_file.exists():
        print_error("Archivo logs/api.log no existe")
        return False
    
    try:
        with open(log_file, 'r') as f:
            lines = f.readlines()
            count = len(lines)
            
            if count == 0:
                print_warning("Archivo de logs está vacío")
                return False
            elif count < 50:
                print_warning(f"Archivo tiene {count} logs (mínimo requerido: 50)")
                return False
            else:
                print_success(f"Archivo de logs tiene {count} registros")
                return True
    except Exception as e:
        print_error(f"Error al leer archivo de logs: {str(e)}")
        return False

def check_docker_containers():
    """Verifica que los contenedores de Docker estén corriendo"""
    import subprocess
    
    try:
        result = subprocess.run(
            ['docker-compose', 'ps', '--services', '--filter', 'status=running'],
            capture_output=True,
            text=True
        )
        
        running_services = result.stdout.strip().split('\n')
        expected_services = [
            'elasticsearch',
            'kibana',
            'filebeat',
            'heartbeat',
            'api'
        ]
        
        all_running = True
        for service in expected_services:
            if service in running_services:
                print_success(f"Contenedor '{service}' está corriendo")
            else:
                print_error(f"Contenedor '{service}' NO está corriendo")
                all_running = False
        
        return all_running
        
    except FileNotFoundError:
        print_warning("docker-compose no encontrado, saltando verificación")
        return None
    except Exception as e:
        print_error(f"Error al verificar contenedores: {str(e)}")
        return False

def main():
    print_header("VERIFICACIÓN DEL SISTEMA ELK")
    print_info("Santa Ana AgroForms - Monitoreo")
    
    results = {
        'docker': None,
        'elasticsearch': False,
        'kibana': False,
        'api': False,
        'indices': False,
        'logs': False
    }
    
    # Verificar contenedores Docker
    print("\n📦 Verificando contenedores Docker...")
    results['docker'] = check_docker_containers()
    
    # Esperar un momento para que los servicios estén listos
    if results['docker']:
        print_info("\nEsperando 5 segundos para que los servicios inicien...\n")
        time.sleep(5)
    
    # Verificar servicios
    print("\n🌐 Verificando servicios web...")
    results['elasticsearch'] = check_service(
        "Elasticsearch",
        "http://localhost:9200"
    )
    
    results['kibana'] = check_service(
        "Kibana",
        "http://localhost:5601/api/status",
        expected_status=200
    )
    
    results['api'] = check_service(
        "Django API",
        "http://localhost:8000/api/"
    )
    
    # Verificar índices en Elasticsearch
    if results['elasticsearch']:
        print("\n📊 Verificando índices en Elasticsearch...")
        results['indices'] = check_elasticsearch_indices()
    
    # Verificar archivo de logs
    print("\n📝 Verificando archivo de logs...")
    results['logs'] = check_log_file()
    
    # Resumen final
    print_header("RESUMEN")
    
    total_checks = sum(1 for v in results.values() if v is not None)
    passed_checks = sum(1 for v in results.values() if v is True)
    
    print(f"Verificaciones pasadas: {passed_checks}/{total_checks}\n")
    
    if passed_checks == total_checks:
        print_success("✨ ¡TODO ESTÁ FUNCIONANDO CORRECTAMENTE! ✨\n")
        print_info("Próximos pasos:")
        print("  1. Abrir Kibana: http://localhost:5601")
        print("  2. Generar más logs: python generate_logs.py")
        print("  3. Crear visualizaciones en el dashboard")
        print("  4. Tomar screenshot para el informe\n")
        return 0
    else:
        print_warning("⚠️ ALGUNOS COMPONENTES NO ESTÁN FUNCIONANDO\n")
        print_info("Acciones recomendadas:")
        
        if not results['docker']:
            print("  → Ejecutar: docker-compose up -d")
        
        if not results['api']:
            print("  → Verificar logs: docker-compose logs api")
        
        if not results['elasticsearch']:
            print("  → Verificar: docker-compose logs elasticsearch")
        
        if not results['logs']:
            print("  → Generar logs: python generate_logs.py")
        
        if not results['indices']:
            print("  → Esperar unos minutos y volver a verificar")
            print("  → O generar más logs para crear los índices")
        
        print()
        return 1

if __name__ == "__main__":
    sys.exit(main())
