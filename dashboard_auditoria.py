# dashboard_auditoria.py
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from datetime import datetime, timedelta
import json
from pathlib import Path
from ferramentas_auditoria import FerramentasAuditoriaReal
import time
from typing import Dict

# Configuração da página
st.set_page_config(
    page_title="Dashboard de Auditoria TCU",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

class DashboardAuditoriaTCU:
    """Dashboard interativo para auditoria de código do TCU."""
    
    def __init__(self):
        self.ferramentas = FerramentasAuditoriaReal()
        self.historico_path = Path("historico_auditorias.json")
        self.carregar_historico()
        
    def carregar_historico(self):
        """Carrega histórico de auditorias."""
        if self.historico_path.exists():
            with open(self.historico_path, 'r') as f:
                self.historico = json.load(f)
        else:
            self.historico = []
    
    def salvar_auditoria(self, resultados: Dict):
        """Salva resultados no histórico."""
        self.historico.append(resultados)
        # Manter apenas últimas 100 auditorias
        self.historico = self.historico[-100:]
        
        with open(self.historico_path, 'w') as f:
            json.dump(self.historico, f, indent=2)
    
    def render_sidebar(self):
        """Renderiza barra lateral com filtros e controles."""
        st.sidebar.title("🔍 TCU Audit System")
        st.sidebar.markdown("---")
        
        # Status do sistema
        st.sidebar.subheader("📡 Status do Sistema")
        ferramentas = self.ferramentas.ferramentas_disponiveis
        
        for ferramenta, disponivel in ferramentas.items():
            if disponivel:
                st.sidebar.success(f"✅ {ferramenta.title()}")
            else:
                st.sidebar.error(f"❌ {ferramenta.title()}")
        
        st.sidebar.markdown("---")
        
        # Filtros
        st.sidebar.subheader("🎯 Filtros")
        periodo = st.sidebar.selectbox(
            "Período",
            ["Últimas 24h", "Última semana", "Último mês", "Todo histórico"]
        )
        
        nivel_minimo = st.sidebar.slider(
            "Score mínimo",
            min_value=0,
            max_value=100,
            value=70
        )
        
        st.sidebar.markdown("---")
        
        # Configurações
        st.sidebar.subheader("⚙️ Configurações")
        auto_refresh = st.sidebar.checkbox("Auto-refresh", value=False)
        if auto_refresh:
            refresh_rate = st.sidebar.number_input(
                "Intervalo (segundos)",
                min_value=5,
                max_value=300,
                value=30
            )
            time.sleep(refresh_rate)
            st.rerun()
        
        return periodo, nivel_minimo
    
    def render_metricas_principais(self):
        """Renderiza métricas principais no topo."""
        if not self.historico:
            st.info("Nenhuma auditoria realizada ainda.")
            return
        
        # Calcular métricas
        total_auditorias = len(self.historico)
        aprovadas = sum(1 for h in self.historico if h.get("status") == "APROVADO")
        taxa_aprovacao = (aprovadas / total_auditorias * 100) if total_auditorias > 0 else 0
        
        scores = [h.get("score_geral", 0) for h in self.historico]
        score_medio = sum(scores) / len(scores) if scores else 0
        
        # Últimos 7 dias
        sete_dias_atras = datetime.now() - timedelta(days=7)
        recentes = [
            h for h in self.historico
            if datetime.fromisoformat(h["timestamp"]) > sete_dias_atras
        ]
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "Total Auditorias",
                total_auditorias,
                delta=f"+{len(recentes)} esta semana"
            )
        
        with col2:
            st.metric(
                "Taxa de Aprovação",
                f"{taxa_aprovacao:.1f}%",
                delta=f"{aprovadas} aprovadas"
            )
        
        with col3:
            st.metric(
                "Score Médio",
                f"{score_medio:.1f}",
                delta=f"{score_medio - 70:.1f} vs meta"
            )
        
        with col4:
            # Tempo médio desde última auditoria
            if self.historico:
                ultima = datetime.fromisoformat(self.historico[-1]["timestamp"])
                tempo_desde = datetime.now() - ultima
                st.metric(
                    "Última Auditoria",
                    f"{tempo_desde.seconds // 3600}h atrás",
                    delta=None
                )
    
    def render_grafico_evolucao(self):
        """Renderiza gráfico de evolução temporal."""
        if not self.historico:
            return
        
        # Preparar dados
        dados = []
        for h in self.historico:
            dados.append({
                "timestamp": datetime.fromisoformat(h["timestamp"]),
                "score": h.get("score_geral", 0),
                "status": h.get("status", "DESCONHECIDO")
            })
        
        df = pd.DataFrame(dados)
        df = df.sort_values("timestamp")
        
        # Criar gráfico
        fig = go.Figure()
        
        # Linha de score
        fig.add_trace(go.Scatter(
            x=df["timestamp"],
            y=df["score"],
            mode='lines+markers',
            name='Score',
            line=dict(color='blue', width=2),
            marker=dict(
                size=8,
                color=df["status"].map({"APROVADO": "green", "REPROVADO": "red"})
            )
        ))
        
        # Linha de meta (70)
        fig.add_hline(
            y=70,
            line_dash="dash",
            line_color="orange",
            annotation_text="Meta Mínima (70)"
        )
        
        fig.update_layout(
            title="Evolução do Score de Qualidade",
            xaxis_title="Data/Hora",
            yaxis_title="Score",
            hovermode='x unified',
            height=400
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    def render_distribuicao_issues(self):
        """Renderiza gráfico de distribuição de issues."""
        if not self.historico:
            return
        
        # Agregar issues por tipo
        todas_issues = {
            "Segurança Crítica": 0,
            "Segurança Alta": 0,
            "Segurança Média": 0,
            "Qualidade": 0,
            "Convenções": 0
        }
        
        for h in self.historico:
            if "analises" in h:
                for ferramenta, resultado in h["analises"].items():
                    if ferramenta == "bandit":
                        todas_issues["Segurança Crítica"] += resultado.get("issues_criticas", 0)
                        todas_issues["Segurança Alta"] += resultado.get("issues_altas", 0)
                        todas_issues["Segurança Média"] += resultado.get("issues_medias", 0)
                    elif ferramenta == "pylint":
                        todas_issues["Qualidade"] += resultado.get("errors", 0)
                        todas_issues["Convenções"] += resultado.get("conventions", 0)
        
        # Criar gráfico de pizza
        fig = px.pie(
            values=list(todas_issues.values()),
            names=list(todas_issues.keys()),
            title="Distribuição de Issues por Categoria",
            color_discrete_sequence=px.colors.qualitative.Set3
        )
        
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)
    
    def render_alertas_criticos(self):
        """Renderiza alertas críticos em tempo real."""
        if not self.historico:
            return
        
        st.subheader("🚨 Alertas Críticos")
        
        alertas = []
        ultima = self.historico[-1] if self.historico else None
        
        if ultima:
            # Verificar score baixo
            if ultima.get("score_geral", 0) < 50:
                alertas.append({
                    "tipo": "error",
                    "mensagem": f"Score crítico: {ultima['score_geral']:.1f} - Ação imediata necessária!"
                })
            elif ultima.get("score_geral", 0) < 70:
                alertas.append({
                    "tipo": "warning",
                    "mensagem": f"Score abaixo da meta: {ultima['score_geral']:.1f} - Melhorias recomendadas"
                })
            
            # Verificar issues críticas de segurança
            if "analises" in ultima:
                bandit = ultima["analises"].get("bandit", {})
                if bandit.get("issues_criticas", 0) > 0:
                    alertas.append({
                        "tipo": "error",
                        "mensagem": f"⚠️ {bandit['issues_criticas']} vulnerabilidades críticas detectadas!"
                    })
        
        # Exibir alertas
        for alerta in alertas:
            if alerta["tipo"] == "error":
                st.error(alerta["mensagem"])
            else:
                st.warning(alerta["mensagem"])
        
        if not alertas:
            st.success("✅ Nenhum alerta crítico no momento")
    
    def render_analise_codigo(self):
        """Renderiza área de input e análise de código."""
        st.subheader("📝 Análise de Código em Tempo Real")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            codigo = st.text_area(
                "Cole o código Python para análise:",
                height=300,
                placeholder="def processar_dados(dados):\n    # Seu código aqui\n    return resultado"
            )
            
            if st.button("🔍 Executar Auditoria Completa", type="primary"):
                if codigo:
                    with st.spinner("Executando análise completa..."):
                        resultados = self.ferramentas.auditoria_completa(codigo)
                        self.salvar_auditoria(resultados)
                        
                        # Exibir resultados
                        st.success(f"Análise concluída! Status: {resultados['status']}")
                        
                        # Score geral
                        score = resultados['score_geral']
                        color = "green" if score >= 70 else "orange" if score >= 50 else "red"
                        st.markdown(f"### Score Geral: :{color}[{score:.1f}/100]")
                        
                        # Detalhes por ferramenta
                        with st.expander("📊 Ver detalhes da análise", expanded=True):
                            for ferramenta, resultado in resultados["analises"].items():
                                st.write(f"**{ferramenta.upper()}**")
                                if "detalhes" in resultado and resultado["detalhes"]:
                                    for detalhe in resultado["detalhes"][:3]:
                                        st.write(f"  • {detalhe}")
                                st.write("---")
        
        with col2:
            st.subheader("📋 Checklist TCU")
            
            checklist = {
                "Tratamento de Erros": False,
                "Logs Estruturados": False,
                "Documentação": False,
                "Segurança": False,
                "Performance": False
            }
            
            # Análise básica do código
            if codigo:
                checklist["Tratamento de Erros"] = "try" in codigo and "except" in codigo
                checklist["Logs Estruturados"] = "logging" in codigo or "log" in codigo.lower()
                checklist["Documentação"] = '"""' in codigo or "'''" in codigo
                checklist["Segurança"] = not any(p in codigo.lower() for p in ["eval", "exec", "__import__"])
            
            for item, status in checklist.items():
                if status:
                    st.success(f"✅ {item}")
                else:
                    st.error(f"❌ {item}")
    
    def render_historico_detalhado(self):
        """Renderiza tabela com histórico detalhado."""
        st.subheader("📜 Histórico de Auditorias")
        
        if not self.historico:
            st.info("Nenhuma auditoria no histórico")
            return
        
        # Preparar dados para tabela
        dados_tabela = []
        for h in reversed(self.historico[-10:]):  # Últimas 10
            dados_tabela.append({
                "Data/Hora": datetime.fromisoformat(h["timestamp"]).strftime("%d/%m/%Y %H:%M"),
                "Score": f"{h['score_geral']:.1f}",
                "Status": h["status"],
                "Ferramentas": len(h.get("analises", {})),
                "Issues": sum(
                    r.get("total_issues", 0) 
                    for r in h.get("analises", {}).values()
                )
            })
        
        df = pd.DataFrame(dados_tabela)
        
        # Aplicar estilo condicional
        def color_status(val):
            return 'color: green' if val == 'APROVADO' else 'color: red'
        
        styled_df = df.style.applymap(color_status, subset=['Status'])
        st.dataframe(styled_df, use_container_width=True)
    
    def run(self):
        """Executa o dashboard completo."""
        st.title("🔍 Dashboard de Auditoria de Código - TCU")
        st.markdown("---")
        
        # Sidebar
        periodo, nivel_minimo = self.render_sidebar()
        
        # Layout principal
        tab1, tab2, tab3 = st.tabs(["📊 Visão Geral", "🔬 Análise Detalhada", "📈 Relatórios"])
        
        with tab1:
            self.render_metricas_principais()
            st.markdown("---")
            
            col1, col2 = st.columns(2)
            with col1:
                self.render_grafico_evolucao()
            with col2:
                self.render_distribuicao_issues()
            
            st.markdown("---")
            self.render_alertas_criticos()
        
        with tab2:
            self.render_analise_codigo()
        
        with tab3:
            self.render_historico_detalhado()
            
            # Exportar relatório
            if st.button("📄 Gerar Relatório PDF"):
                st.info("Funcionalidade em desenvolvimento...")
            
            # Download dos dados
            if self.historico:
                json_str = json.dumps(self.historico, indent=2)
                st.download_button(
                    label="📥 Download Histórico (JSON)",
                    data=json_str,
                    file_name=f"auditoria_tcu_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                    mime="application/json"
                )

# Executar dashboard
if __name__ == "__main__":
    dashboard = DashboardAuditoriaTCU()
    dashboard.run()