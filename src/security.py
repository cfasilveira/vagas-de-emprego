# src/security.py
import secrets
import hashlib

def generate_handshake_token():
    """Gera um token único para validar a sessão de troca de dados."""
    return secrets.token_hex(32)

def verify_integrity(data, received_hash):
    """Verifica se os dados foram alterados durante o trânsito[cite: 40]."""
    calculated_hash = hashlib.sha256(str(data).encode()).hexdigest()
    return calculated_hash == received_hash

# Exemplo de uso de POO para robustez [cite: 40]
class SecurityGate:
    @staticmethod
    def validate_input(text: str):
        """Bloqueia caracteres suspeitos de injeção/ataque[cite: 38, 45]."""
        blacklist = [";", "--", "DROP", "SELECT", "INSERT", "<script>"]
        return not any(item in text.upper() for item in blacklist)
