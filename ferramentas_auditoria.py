# ferramentas_auditoria.py
import ast
import subprocess
import tempfile
import json
import re
from pathlib import Path
from typing import Dict, List, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime

@dataclass
class ResultadoSeguranca:
    """Estrutura para resultados de análise de segurança."""
    ferramenta: str
    issues_criticas: int
    issues_altas: int
    issues_medias: int
    issues_baixas: int
    detalhes: List[str]
    score_seguranca: float

class FerramentasAuditoriaReal:
    """Integração com ferramentas reais de análise de código."""
    
    def __init__(self):
        self.ferramentas_disponiveis = self._verificar_ferramentas()
        
    def _verificar_ferramentas(self) -> Dict[str, bool]:
        """Verifica quais ferramentas estão instaladas."""
        ferramentas = {}
        
        # Verificar Bandit
        try:
            subprocess.run(["bandit", "--version"], capture_output=True, timeout=5)
            ferramentas["bandit"] = True
        except:
            ferramentas["bandit"] = False
            
        # Verificar Safety
        try:
            subprocess.run(["safety", "--version"], capture_output=True, timeout=5)
            ferramentas["safety"] = True
        except:
            ferramentas["safety"] = False
            
        # Verificar Semgrep
        try:
            subprocess.run(["semgrep", "--version"], capture_output=True, timeout=5)
            ferramentas["semgrep"] = True
        except:
            ferramentas["semgrep"] = False
            
        # Verificar Pylint
        try:
            subprocess.run(["pylint", "--version"], capture_output=True, timeout=5)
            ferramentas["pylint"] = True
        except:
            ferramentas["pylint"] = False
            
        return ferramentas
    
    def executar_bandit(self, codigo: str) -> ResultadoSeguranca:
        """Executa análise de segurança com Bandit."""
        if not self.ferramentas_disponiveis["bandit"]:
            return ResultadoSeguranca(
                ferramenta="Bandit",
                issues_criticas=0,
                issues_altas=0,
                issues_medias=0,
                issues_baixas=0,
                detalhes=["Bandit não instalado"],
                score_seguranca=0.0
            )
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(codigo)
            f.flush()
            
            try:
                # Executar Bandit com output JSON
                resultado = subprocess.run(
                    ["bandit", "-r", "-f", "json", f.name],
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                
                if resultado.returncode == 0 and resultado.stdout:
                    data = json.loads(resultado.stdout)
                    
                    issues = data.get("results", [])
                    criticas = sum(1 for i in issues if i["issue_severity"] == "HIGH")
                    altas = sum(1 for i in issues if i["issue_severity"] == "MEDIUM")
                    medias = sum(1 for i in issues if i["issue_severity"] == "LOW")
                    
                    detalhes = [
                        f"{i['test_name']}: {i['issue_text']} (Linha {i['line_number']})"
                        for i in issues[:10]  # Limitar a 10 issues
                    ]
                    
                    score = max(0, 100 - (criticas * 25 + altas * 10 + medias * 5))
                    
                    return ResultadoSeguranca(
                        ferramenta="Bandit",
                        issues_criticas=criticas,
                        issues_altas=altas,
                        issues_medias=medias,
                        issues_baixas=0,
                        detalhes=detalhes,
                        score_seguranca=score
                    )
            except Exception as e:
                return ResultadoSeguranca(
                    ferramenta="Bandit",
                    issues_criticas=0,
                    issues_altas=0,
                    issues_medias=0,
                    issues_baixas=0,
                    detalhes=[f"Erro na execução: {str(e)}"],
                    score_seguranca=0.0
                )
            finally:
                Path(f.name).unlink(missing_ok=True)
    
    def executar_pylint(self, codigo: str) -> Dict:
        """Executa análise de qualidade com Pylint."""
        if not self.ferramentas_disponiveis["pylint"]:
            return {"score": 0, "issues": 0, "detalhes": ["Pylint não instalado"]}
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(codigo)
            f.flush()
            
            try:
                resultado = subprocess.run(
                    ["pylint", f.name, "--output-format=json"],
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                
                if resultado.stdout:
                    issues = json.loads(resultado.stdout)
                    
                    # Categorizar por tipo
                    errors = sum(1 for i in issues if i["type"] == "error")
                    warnings = sum(1 for i in issues if i["type"] == "warning")
                    conventions = sum(1 for i in issues if i["type"] == "convention")
                    
                    score = max(0, 10.0 - (errors * 2 + warnings * 0.5 + conventions * 0.1))
                    
                    return {
                        "score": round(score, 2),
                        "errors": errors,
                        "warnings": warnings,
                        "conventions": conventions,
                        "total_issues": len(issues),
                        "detalhes": [f"{i['symbol']}: {i['message']}" for i in issues[:5]]
                    }
            except Exception as e:
                return {"score": 0, "issues": 0, "detalhes": [f"Erro: {str(e)}"]}
            finally:
                Path(f.name).unlink(missing_ok=True)
    
    def analisar_dependencias(self, requirements: str = None) -> Dict:
        """Analisa vulnerabilidades em dependências com Safety."""
        if not self.ferramentas_disponiveis["safety"]:
            return {"vulnerabilidades": 0, "detalhes": ["Safety não instalado"]}
        
        try:
            # Se não tiver requirements, verificar pacotes comuns
            resultado = subprocess.run(
                ["safety", "check", "--json"],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if resultado.stdout:
                data = json.loads(resultado.stdout)
                vulnerabilidades = data.get("vulnerabilities", [])
                
                criticas = sum(1 for v in vulnerabilidades if v["severity"] == "critical")
                altas = sum(1 for v in vulnerabilidades if v["severity"] == "high")
                
                return {
                    "total_vulnerabilidades": len(vulnerabilidades),
                    "criticas": criticas,
                    "altas": altas,
                    "score": max(0, 100 - (criticas * 30 + altas * 15)),
                    "detalhes": [
                        f"{v['package_name']} {v['vulnerable_spec']}: {v['advisory']}"
                        for v in vulnerabilidades[:5]
                    ]
                }
        except Exception as e:
            return {"vulnerabilidades": 0, "detalhes": [f"Erro: {str(e)}"]}
        
        return {"vulnerabilidades": 0, "detalhes": []}
    
    def executar_semgrep(self, codigo: str) -> Dict:
        """Executa análise com Semgrep para padrões de segurança."""
        if not self.ferramentas_disponiveis["semgrep"]:
            return {"findings": 0, "detalhes": ["Semgrep não instalado"]}
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(codigo)
            f.flush()
            
            try:
                resultado = subprocess.run(
                    ["semgrep", "--config", "p/python", "--json", f.name],
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                
                if resultado.stdout:
                    data = json.loads(resultado.stdout)
                    findings = data.get("results", [])
                    
                    criticos = sum(1 for f in findings if f["extra"]["severity"] == "ERROR")
                    warnings = sum(1 for f in findings if f["extra"]["severity"] == "WARNING")
                    
                    return {
                        "total_findings": len(findings),
                        "criticos": criticos,
                        "warnings": warnings,
                        "score": max(0, 100 - (criticos * 20 + warnings * 5)),
                        "detalhes": [
                            f"{f['check_id']}: {f['extra']['message']}"
                            for f in findings[:5]
                        ]
                    }
            except Exception as e:
                return {"findings": 0, "detalhes": [f"Erro: {str(e)}"]}
            finally:
                Path(f.name).unlink(missing_ok=True)
    
    def auditoria_completa(self, codigo: str) -> Dict:
        """Executa todas as ferramentas de auditoria."""
        
        resultados = {
            "timestamp": datetime.now().isoformat(),
            "ferramentas_disponiveis": self.ferramentas_disponiveis,
            "analises": {}
        }
        
        # Executar todas as ferramentas
        if self.ferramentas_disponiveis["bandit"]:
            resultados["analises"]["bandit"] = asdict(self.executar_bandit(codigo))
            
        if self.ferramentas_disponiveis["pylint"]:
            resultados["analises"]["pylint"] = self.executar_pylint(codigo)
            
        if self.ferramentas_disponiveis["semgrep"]:
            resultados["analises"]["semgrep"] = self.executar_semgrep(codigo)
            
        if self.ferramentas_disponiveis["safety"]:
            resultados["analises"]["safety"] = self.analisar_dependencias()
        
        # Calcular score geral
        scores = []
        for analise in resultados["analises"].values():
            if "score" in analise:
                scores.append(analise["score"])
            elif "score_seguranca" in analise:
                scores.append(analise["score_seguranca"])
        
        resultados["score_geral"] = sum(scores) / len(scores) if scores else 0
        resultados["status"] = "APROVADO" if resultados["score_geral"] >= 70 else "REPROVADO"
        
        return resultados