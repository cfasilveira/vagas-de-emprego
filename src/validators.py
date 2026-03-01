# src/validators.py
import re
from pydantic import BaseModel, validator, Field
from typing import Literal

class CandidatoSchema(BaseModel):
    """Esquema de validação para garantir a integridade dos dados do candidato."""
    nome_completo: str = Field(..., min_length=3, max_length=100)
    documento: str  # RG ou CPF
    celular: str
    genero: Literal["M", "F"]

    @validator('nome_completo')
    def validar_nome(cls, v):
        # Proteção contra scripts e caracteres especiais (Hacker-proof)
        if not re.match(r"^[a-zA-ZÀ-ÿ\s]+$", v):
            raise ValueError("O nome deve conter apenas letras.")
        return v.strip()

    @validator('documento')
    def validar_documento(cls, v):
        # Remove caracteres não numéricos para padronização no banco
        nums = re.sub(r"\D", "", v)
        if len(nums) < 7 or len(nums) > 11:
            raise ValueError("Documento (CPF ou RG) inválido. Insira apenas números.")
        return nums

    @validator('celular')
    def validar_celular(cls, v):
        # Validação para formato (XX) 9XXXX-XXXX ou apenas números
        nums = re.sub(r"\D", "", v)
        if len(nums) < 10 or len(nums) > 11:
            raise ValueError("Celular/WhatsApp inválido. Use o formato com DDD.")
        return nums

class VagaSchema(BaseModel):
    """Validação para o cadastro de vagas pelo Administrador."""
    nome: str
    descricao: str
    salario: float
    beneficios: str
    data_termino: str # Validada posteriormente como objeto date

    @validator('salario')
    def salario_positivo(cls, v):
        if v < 0:
            raise ValueError("O salário não pode ser negativo.")
        return v
