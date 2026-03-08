import bcrypt

class Security:
    @staticmethod
    def gerar_senha_hash(senha_plana: str) -> str:
        """Gera um hash seguro usando Bcrypt (Referência: Troy Hunt)."""
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(senha_plana.encode('utf-8'), salt).decode('utf-8')

    @staticmethod
    def verificar_senha(senha_plana: str, hash_armazenado: str) -> bool:
        """Verifica se a senha plana corresponde ao hash armazenado."""
        try:
            return bcrypt.checkpw(senha_plana.encode('utf-8'), hash_armazenado.encode('utf-8'))
        except Exception:
            return False

    @staticmethod
    def mascarar_cpf(cpf: str) -> str:
        """
        Mascaramento para conformidade LGPD.
        Exemplo: 123.456.789-01 -> ***.456.***-01
        """
        if not cpf or len(cpf) < 14:
            return cpf
        # Preserva o segundo bloco e os últimos dois dígitos
        return f"***.{cpf[4:7]}.***-{cpf[-2:]}"
