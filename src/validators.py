import re
from pydantic import BaseModel, field_validator

class CandidatoSchema(BaseModel):
    nome: str
    email: str
    documento: str
    celular: str
    resumo: str # Adicionado

    @field_validator('email')
    @classmethod
    def validar_email(cls, v: str) -> str:
        if not re.match(r"^\S+@\S+\.\S+$", v):
            raise ValueError("E-mail inválido. Use o formato nome@dominio.com")
        return v.lower().strip()

    @field_validator('celular', 'documento')
    @classmethod
    def limpar_numeros(cls, v: str) -> str:
        nums = re.sub(r"\D", "", v)
        if len(nums) < 7:
            raise ValueError("O campo deve conter números válidos.")
        return nums

    @field_validator('resumo')
    @classmethod
    def validar_resumo(cls, v: str) -> str:
        # Garante que o Mistral-Nemo receba conteúdo útil
        texto_limpo = v.strip()
        if len(texto_limpo) < 20:
            raise ValueError("O resumo profissional deve ter ao menos 20 caracteres.")
        return texto_limpo

class VagaSchema(BaseModel):
    titulo: str
    cidade: str
    salario: float

    @field_validator('salario')
    @classmethod
    def salario_positivo(cls, v: float) -> float:
        if v <= 0:
            raise ValueError("O salário deve ser superior a zero.")
        return v
