# ============================================
# CONFIGURACIÓN DE LOGGING PARA ELK STACK
# ============================================
# Agregar esto al final de tu settings.py

import os
from pathlib import Path

# Crear directorio de logs si no existe
LOGS_DIR = BASE_DIR / 'logs'
LOGS_DIR.mkdir(exist_ok=True)

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    
    # Formateadores
    'formatters': {
        'json': {
            '()': 'pythonjsonlogger.jsonlogger.JsonFormatter',
            'format': '%(asctime)s %(name)s %(levelname)s %(message)s',
            'rename_fields': {
                'asctime': '@timestamp',
                'levelname': 'log.level',
                'name': 'logger.name',
            }
        },
        'verbose': {
            'format': '{levelname} {asctime} {module} {message}',
            'style': '{',
        },
    },
    
    # Handlers
    'handlers': {
        # Handler para logs en archivo JSON (para Filebeat)
        'file_json': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': LOGS_DIR / 'api.log',
            'maxBytes': 10485760,  # 10MB
            'backupCount': 5,
            'formatter': 'json',
        },
        # Handler para consola (útil en desarrollo)
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    
    # Loggers
    'loggers': {
        # Logger para requests de la API
        'api.requests': {
            'handlers': ['file_json', 'console'],
            'level': 'INFO',
            'propagate': False,
        },
        # Logger para Django
        'django': {
            'handlers': ['file_json', 'console'],
            'level': 'INFO',
            'propagate': False,
        },
        # Logger para tu app
        'formularios': {
            'handlers': ['file_json', 'console'],
            'level': 'INFO',
            'propagate': False,
        },
    },
    
    # Root logger
    'root': {
        'handlers': ['file_json', 'console'],
        'level': 'INFO',
    },
}

# ============================================
# FIN DE CONFIGURACIÓN DE LOGGING
# ============================================
