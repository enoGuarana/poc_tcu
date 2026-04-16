# 🔍 Sistema de Auditoria Automática de Código - TCU

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-red.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)
![Status](https://img.shields.io/badge/Status-Produção-brightgreen.svg)

## 📌 O que é este projeto?

Um **robô auditor de código** que analisa automaticamente programas Python seguindo as normas do Tribunal de Contas da União (TCU). 

**Problema que resolve:** Antes, auditores humanos precisavam ler centenas de linhas de código manualmente. Agora, um sistema automatizado faz isso em segundos!

**Público-alvo:** 
- 🏛️ Órgãos públicos que precisam de código auditado
- 👨‍💻 Desenvolvedores que querem validar código antes de enviar
- 📊 Auditores do TCU que precisam otimizar seu trabalho

---

## 🎯 Funcionalidades Principais

### ✅ Análise Automática
- Verifica tratamento de erros (`try/except`)
- Detecta presença de sistema de logs
- Avalia documentação do código
- Identifica vulnerabilidades de segurança

### 📊 Dashboard Interativo
- Gráficos de evolução da qualidade
- Métricas em tempo real
- Histórico completo de auditorias
- Exportação de relatórios

### 🔒 Segurança
- Integração com Bandit (análise de segurança)
- Verificação de dependências vulneráveis
- Detecção de padrões perigosos (`eval`, `exec`)

---

## 🚀 Como Instalar e Executar

### 📦 Pré-requisitos

```bash
# Verifique se tem Python instalado
python --version  # Precisa ser 3.8 ou superior

# Instale o gerenciador de pacotes (se não tiver)
pip --version
