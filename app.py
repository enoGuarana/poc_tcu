# app.py - VERSÃO SIMPLIFICADA PARA TESTE RÁPIDO
import streamlit as st
import json
from pathlib import Path
from datetime import datetime

# Configuração da página
st.set_page_config(
    page_title="Auditoria TCU - Teste",
    page_icon="🔍",
    layout="wide"
)

st.title("🔍 Sistema de Auditoria TCU - Versão de Teste")
st.markdown("---")

# Sidebar
st.sidebar.title("📋 Configurações")
modo_teste = st.sidebar.checkbox("Modo Simulação", value=True, 
                                help="Usa dados simulados sem precisar instalar ferramentas")

# Área principal
tab1, tab2 = st.tabs(["📝 Análise", "📊 Histórico"])

with tab1:
    st.subheader("Análise de Código Python")
    
    # Exemplo de código
    codigo_exemplo = '''import logging

def processar_dados_financeiros(dados):
    """Processa dados financeiros conforme normas TCU"""
    logger = logging.getLogger(__name__)
    
    try:
        if not dados:
            raise ValueError("Lista de dados vazia")
        
        logger.info(f"Processando {len(dados)} registros")
        total = sum(dados)
        media = total / len(dados)
        
        return {"total": total, "media": media}
        
    except Exception as e:
        logger.error(f"Erro no processamento: {e}")
        raise
'''
    
    codigo = st.text_area(
        "Cole o código para análise:",
        value=codigo_exemplo,
        height=300
    )
    
    if st.button("🔍 Analisar Código", type="primary"):
        with st.spinner("Analisando..."):
            
            if modo_teste:
                # Simulação de análise
                score = 85 if "try" in codigo and "except" in codigo else 45
                status = "APROVADO" if score >= 70 else "REPROVADO"
                
                st.success(f"Análise concluída! Status: {status}")
                
                # Score
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Score Geral", f"{score}/100")
                with col2:
                    st.metric("Status", status)
                with col3:
                    st.metric("Ferramentas", "2/4 disponíveis")
                
                # Checklist
                st.subheader("📋 Checklist TCU")
                col1, col2 = st.columns(2)
                
                with col1:
                    if "try" in codigo:
                        st.success("✅ Tratamento de Erros")
                    else:
                        st.error("❌ Tratamento de Erros")
                    
                    if "logging" in codigo:
                        st.success("✅ Sistema de Logs")
                    else:
                        st.error("❌ Sistema de Logs")
                
                with col2:
                    if '"""' in codigo:
                        st.success("✅ Documentação")
                    else:
                        st.error("❌ Documentação")
                    
                    if "eval" not in codigo and "exec" not in codigo:
                        st.success("✅ Segurança Básica")
                    else:
                        st.error("❌ Vulnerabilidades")
                
            else:
                # Modo real
                try:
                    from ferramentas_auditoria import FerramentasAuditoriaReal
                    ferramentas = FerramentasAuditoriaReal()
                    resultado = ferramentas.auditoria_completa(codigo)
                    
                    st.success(f"Análise real concluída! Status: {resultado['status']}")
                    st.json(resultado)
                    
                except ImportError:
                    st.error("Módulo ferramentas_auditoria não encontrado. Use o modo simulação.")

with tab2:
    st.subheader("Histórico de Auditorias")
    
    # Dados de exemplo
    historico_exemplo = [
        {"data": "2024-01-15 10:30", "score": 85, "status": "APROVADO"},
        {"data": "2024-01-15 09:15", "score": 45, "status": "REPROVADO"},
        {"data": "2024-01-14 16:20", "score": 92, "status": "APROVADO"},
    ]
    
    st.dataframe(historico_exemplo, use_container_width=True)

# Rodapé
st.markdown("---")
st.markdown("### 📌 Instruções")
st.markdown("""
1. **Modo Simulação**: Funciona sem instalar ferramentas adicionais
2. **Modo Real**: Requer instalação das ferramentas de auditoria
3. Cole seu código Python e clique em "Analisar Código"
""")