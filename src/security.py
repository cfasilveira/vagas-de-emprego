import bcrypt

class Security:
    @staticmethod
    def gerar_senha_hash(senha_plana: str) -> str:
        """Gera um hash seguro usando Bcrypt."""
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(senha_plana.encode('utf-8'), salt).decode('utf-8')

    @staticmethod
    def verificar_senha(senha_plana: str, hash_armazenado: str) -> bool:
        """Verifica se a senha plana corresponde ao hash armazenado."""
        try:
            # Garante que ambos sejam comparados como bytes
            return bcrypt.checkpw(
                senha_plana.encode('utf-8'), 
                hash_armazenado.encode('utf-8')
            )
        except Exception as e:
            print(f"Erro na verificação de senha: {e}")
            return False

    @staticmethod
    def mascarar_cpf(cpf: str) -> str:
        """Mascaramento para conformidade LGPD."""
        if not cpf or len(cpf) < 14:
            return cpf
        return f"***.{cpf[4:7]}.***-{cpf[-2:]}"
