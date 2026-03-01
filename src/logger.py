import logging
import os

# Configura o log para sair no console e em arquivo
log_format = "%(asctime)s - %(levelname)s - %(message)s"
logging.basicConfig(level=logging.INFO, format=log_format)

logger = logging.getLogger("VagasSegura")

def log_audit(event: str):
    """Registra eventos de segurança e integridade."""
    logger.info(f"[AUDIT] {event}")

def log_error(error: str):
    """Registra falhas técnicas."""
    logger.error(f"[ERROR] {error}")
