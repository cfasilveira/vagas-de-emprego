---
title: RH Inteligente IA
emoji: 🎯
colorFrom: blue
colorTo: indigo
sdk: streamlit
sdk_version: 1.32.0
app_file: main.py
pinned: false
---

# 🎯 RH Inteligente: Gestão de Vagas com IA

Sistema moderno de recrutamento e seleção que utiliza Inteligência Artificial (Gemini ou Ollama) para análise de candidatos e Dashboard de BI.

## 🚀 Tecnologias
- **IA:** Google GenAI (Gemini) / Ollama
- **DB:** PostgreSQL + SQLAlchemy
- **Painel:** Streamlit + Plotly Express (Clean Design)

## 🛠️ Configuração na Nuvem (Hugging Face)
Para o funcionamento correto, configura as **Variables and Secrets** no painel do Space:
1. `DATABASE_URL`: URL do teu banco PostgreSQL externo (ex: Supabase, Render, Neon).
2. `GOOGLE_API_KEY`: Tua chave do Gemini (opcional, ativa o modo nuvem).

## 🌟 Como o Deploy funciona
Este Space utiliza o SDK nativo do Streamlit. O arquivo principal é o `main.py` e as dependências são geridas automaticamente a partir do `pyproject.toml` via `uv`.

---
