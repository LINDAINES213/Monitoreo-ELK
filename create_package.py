"""
Script para preparar los entregables del proyecto ELK
Crea un archivo ZIP con todos los archivos necesarios
"""

import os
import shutil
from datetime import datetime
from pathlib import Path
import zipfile

def create_deliverables():
    """Crea el paquete de entregables para el proyecto"""
    
    # Nombre del archivo ZIP
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    zip_filename = f"Proyecto_ELK_Fase3_{timestamp}.zip"
    
    # Archivos a incluir
    files_to_include = [
        "docker-compose.yml",
        "filebeat.yml",
        "heartbeat.yml",
        "backend/middlewares/logging_middleware.py",
        "README_ELK.md",
        "generate_logs.py",
        "verify_elk.py",
    ]
    
    # Archivos opcionales (si existen)
    optional_files = [
        "logs/api.log",  # Muestra de logs (primeras 100 líneas)
        "dashboard_screenshot.png",  # Screenshot del dashboard
        "informe_tecnico.pdf",  # Informe técnico
    ]
    
    print("=" * 60)
    print("📦 PREPARANDO ENTREGABLES DEL PROYECTO")
    print("=" * 60)
    print()
    
    # Crear carpeta temporal
    temp_dir = Path("entregables_elk")
    if temp_dir.exists():
        shutil.rmtree(temp_dir)
    temp_dir.mkdir()
    
    print("📁 Copiando archivos...")
    
    # Copiar archivos principales
    copied_files = []
    missing_files = []
    
    for file_path in files_to_include:
        src = Path(file_path)
        if src.exists():
            # Crear estructura de carpetas si es necesario
            dst = temp_dir / file_path
            dst.parent.mkdir(parents=True, exist_ok=True)
            
            shutil.copy2(src, dst)
            print(f"  ✓ {file_path}")
            copied_files.append(file_path)
        else:
            print(f"  ✗ {file_path} (no encontrado)")
            missing_files.append(file_path)
    
    # Copiar archivos opcionales
    print("\n📄 Archivos opcionales:")
    for file_path in optional_files:
        src = Path(file_path)
        if src.exists():
            dst = temp_dir / file_path
            dst.parent.mkdir(parents=True, exist_ok=True)
            
            # Para logs, copiar solo las primeras 100 líneas
            if file_path == "logs/api.log":
                with open(src, 'r') as f_in:
                    lines = f_in.readlines()[:100]
                with open(dst, 'w') as f_out:
                    f_out.writelines(lines)
                print(f"  ✓ {file_path} (primeras 100 líneas)")
            else:
                shutil.copy2(src, dst)
                print(f"  ✓ {file_path}")
        else:
            print(f"  ⚠ {file_path} (no encontrado, pero opcional)")
    
    # Crear archivo README con instrucciones
    readme_content = """# Entregables - Proyecto Fase 3: Monitoreo (ELK)

## Contenido del paquete

### Archivos de configuración:
- `docker-compose.yml` - Configuración del stack ELK completo
- `filebeat.yml` - Configuración de recolección de logs
- `heartbeat.yml` - Configuración de monitoreo de disponibilidad

### Código fuente:
- `backend/middlewares/logging_middleware.py` - Middleware para logging automático

### Scripts:
- `generate_logs.py` - Script para generar logs de prueba
- `verify_elk.py` - Script de verificación del sistema

### Documentación:
- `README_ELK.md` - Documentación completa del proyecto
- `logs/api.log` - Muestra de logs generados (100 primeras líneas)
- `dashboard_screenshot.png` - Captura del dashboard (si está disponible)
- `informe_tecnico.pdf` - Informe técnico completo (si está disponible)

## Instrucciones de instalación

Ver archivo `README_ELK.md` para instrucciones detalladas.

## Autores

- Santa Ana AgroForms Team
- Universidad del Valle de Guatemala
- CC3047 - Administración y Mantenimiento de Sistemas

Fecha: """ + datetime.now().strftime("%Y-%m-%d") + """
"""
    
    with open(temp_dir / "LEEME.txt", 'w', encoding='utf-8') as f:
        f.write(readme_content)
    
    # Crear ZIP
    print(f"\n📦 Creando archivo ZIP: {zip_filename}")
    with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(temp_dir):
            for file in files:
                file_path = Path(root) / file
                arcname = file_path.relative_to(temp_dir)
                zipf.write(file_path, arcname)
    
    # Limpiar carpeta temporal
    shutil.rmtree(temp_dir)
    
    # Resumen
    print("\n" + "=" * 60)
    print("✅ EMPAQUETADO COMPLETADO")
    print("=" * 60)
    print(f"\n📦 Archivo creado: {zip_filename}")
    print(f"📊 Archivos incluidos: {len(copied_files) + 1}")  # +1 por LEEME.txt
    
    if missing_files:
        print("\n⚠️ Archivos faltantes:")
        for file in missing_files:
            print(f"  - {file}")
        print("\nAsegúrate de incluirlos manualmente si son necesarios.")
    
    print("\n📋 Checklist final:")
    print("  [ ] Verificar que el archivo ZIP se creó correctamente")
    print("  [ ] Agregar screenshot del dashboard (dashboard_screenshot.png)")
    print("  [ ] Agregar informe técnico (informe_tecnico.pdf)")
    print("  [ ] Verificar que logs/api.log tiene al menos 50 registros")
    print()

if __name__ == "__main__":
    create_deliverables()
