import json
import re
from pathlib import Path

BASE_DIR = Path(r"c:\Users\Junior do Titico\Desktop\TJPE-2026")

def load_cronograma():
    with open(BASE_DIR / "cronograma_tjpe_fgv.json", "r", encoding="utf-8") as f:
        return json.load(f)

def load_mapeamento():
    text = (BASE_DIR / "mapeamento.json").read_text(encoding="utf-8")
    disciplines = []
    
    disc_pattern = re.compile(
        r'\{\s*id:\s*"(?P<id>[^"]+)",\s*name:\s*"(?P<name>[^"]+)",\s*totalQuestions:\s*(?P<total>\d+),\s*subtopics:\s*\[(?P<subs>.*?)\]\s*\}',
        re.S,
    )
    sub_pattern = re.compile(
        r'\{\s*id:\s*"(?P<id>[^"]+)",\s*name:\s*"(?P<name>[^"]+)",\s*questions:\s*(?P<questions>\d+),\s*percentage:\s*(?P<percentage>[\d.]+)\s*\}'
    )
    
    for dm in disc_pattern.finditer(text):
        subs = []
        for sm in sub_pattern.finditer(dm.group("subs")):
            subs.append({
                "id": sm.group("id"),
                "name": sm.group("name"),
                "questions": int(sm.group("questions")),
                "percentage": float(sm.group("percentage"))
            })
        disciplines.append({
            "id": dm.group("id"),
            "name": dm.group("name"),
            "totalQuestions": int(dm.group("total")),
            "subtopics": subs
        })
    return disciplines

def generate_cronograma_md(cron):
    lines = []
    meta = cron.get("metadata", {})
    lines.append("# Cronograma Completo de Estudos - TJ-PE Magistratura FGV 2026")
    lines.append("")
    lines.append("## Metadados e Diretrizes Estratégicas")
    lines.append("")
    lines.append(f"- **Concurso**: {meta.get('exam')}")
    lines.append(f"- **Período**: {meta.get('startDate')} a {meta.get('endDate')} ({meta.get('totalDays')} dias corridos)")
    lines.append(f"- **Carga Horária**: {meta.get('weekdayMinutes')} minutos (segunda a sexta) e {meta.get('weekendMinutes')} minutos (finais de semana)")
    lines.append(f"- **Início das Revisões Sistemáticas**: Dia {meta.get('revisionStartsOnDay')} (30% da carga diária devotada a revisões)")
    lines.append("")
    
    lines.append("## Ranking Estatístico das Disciplinas (Banca FGV)")
    lines.append("")
    lines.append("| Rank | Disciplina | Total de Questões | Média por Prova |")
    lines.append("| :---: | :--- | :---: | :---: |")
    for d in cron.get("disciplineRanking", []):
        lines.append(f"| {d['rank']} | {d['name']} | {d['totalQuestions']} | {d['averagePerExam']:.2f} |")
    lines.append("")
    
    lines.append("## Matriz Semanal Fixa de Estudos")
    lines.append("")
    lines.append("| Dia da Semana | Disciplina 1 | Disciplina 2 | Tempo Inicial | Tempo após D08 |")
    lines.append("| :--- | :--- | :--- | :--- | :--- |")
    weekdays_order = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
    pt_weekdays = {
        "monday": "Segunda-feira", "tuesday": "Terça-feira", "wednesday": "Quarta-feira",
        "thursday": "Quinta-feira", "friday": "Sexta-feira", "saturday": "Sábado", "sunday": "Domingo"
    }
    for w in weekdays_order:
        pair = cron.get("weeklyPairings", {}).get(w, ["", ""])
        if w in ["saturday", "sunday"]:
            t_ini = "120 min / 120 min"
            t_rev = "92 min / 76 min (rev: 72 min)"
        else:
            t_ini = "90 min / 90 min"
            t_rev = "70 min / 56 min (rev: 54 min)"
        lines.append(f"| {pt_weekdays[w]} | {pair[0]} | {pair[1]} | {t_ini} | {t_rev} |")
    lines.append("")
    
    lines.append("## Estratégia dos 4 Ciclos")
    lines.append("")
    for c in cron.get("cycleStrategy", []):
        lines.append(f"### {c['title']}")
        for act in c["activities"]:
            lines.append(f"- {act}")
        lines.append("")
        
    current_cycle = None
    lines.append("## Cronograma Diário Progressivo (Dias 001 a 108)")
    lines.append("")
    
    for day in cron.get("days", []):
        cycle = day["cycle"]
        if cycle != current_cycle:
            current_cycle = cycle
            c_info = next((c for c in cron.get("cycleStrategy", []) if c["cycle"] == cycle), None)
            title = c_info["title"] if c_info else f"Ciclo {cycle}"
            lines.append(f"### {title}")
            lines.append("")
            
        d_num = day["dayNumber"]
        lines.append(f"#### Dia {d_num:03d} - {day['date']} ({day['weekdayPt'].capitalize()})")
        lines.append(f"- **Ciclo**: {day['cycle']} | **Tempo Total**: {day['totalMinutes']} min (Estudo Novo: {day['newStudyMinutes']} min | Revisão: {day['revisionMinutes']} min)")
        
        for idx, sub in enumerate(day.get("subjects", []), start=1):
            top_str = ", ".join(sub.get("subtopics", []))
            act_str = "; ".join(sub.get("activities", []))
            lines.append(f"- **Matéria {idx}**: {sub['name']} ({sub['minutes']} min) - *Tópico*: {top_str}. *Atividades*: {act_str}")
            
        rev = day.get("revisionPlan")
        if rev:
            items_str = []
            for item in rev.get("items", []):
                items_str.append(f"{item['discipline']} ({', '.join(item['subtopics'])})")
            lines.append(f"- **Revisão Obrigatória ({rev['minutes']} min)**: " + " + ".join(items_str) + f". *Método*: {rev.get('items', [{}])[0].get('method', 'Questões e Caderno de Erros')}")
        else:
            lines.append("- **Revisão Obrigatória**: Sem revisão obrigatória (Semana 1 - fase de acúmulo inicial de conteúdo).")
        lines.append("")
        
    return "\n".join(lines)

def generate_mapeamento_md(disciplines):
    lines = []
    lines.append("# Mapeamento Estatístico Verticalizado FGV - TJ-PE 2026")
    lines.append("")
    lines.append("Mapeamento completo e verticalizado de incidência temática das provas de Magistratura Estadual da banca FGV, com quantitativo de questões e percentual histórico de relevância.")
    lines.append("")
    
    total_all_q = sum(d["totalQuestions"] for d in disciplines)
    lines.append(f"**Total de Questões Analisadas no Banco FGV**: {total_all_q} questões em 14 disciplinas.")
    lines.append("")
    
    sorted_disc = sorted(disciplines, key=lambda x: x["totalQuestions"], reverse=True)
    
    for rank, d in enumerate(sorted_disc, start=1):
        perc_share = (d["totalQuestions"] / total_all_q) * 100 if total_all_q else 0
        lines.append(f"## {rank}. {d['name']}")
        lines.append("")
        lines.append(f"- **Identificador**: `{d['id']}`")
        lines.append(f"- **Volume Histórico FGV**: {d['totalQuestions']} questões ({perc_share:.2f}% do total da prova)")
        lines.append(f"- **Total de Subtemas Mapeados**: {len(d['subtopics'])} subtemas")
        lines.append("")
        lines.append("| ID Subtema | Nome do Subtema / Conteúdo Programático | Questões | % na Disciplina |")
        lines.append("| :--- | :--- | :---: | :---: |")
        for sub in d["subtopics"]:
            lines.append(f"| `{sub['id']}` | {sub['name']} | {sub['questions']} | {sub['percentage']:.2f}% |")
        lines.append("")
        
    return "\n".join(lines)

def generate_guia_md(cron):
    lines = []
    lines.append("# Guia de Metodologia e Protocolo de Execução - TJ-PE Magistratura FGV")
    lines.append("")
    lines.append("## 1. Visão Geral da Metodologia")
    lines.append("Este plano foi estruturado para a preparação de alto rendimento para o concurso de Juiz Substituto do Tribunal de Justiça de Pernambuco (TJ-PE), com foco analítico nas peculiaridades da banca FGV.")
    lines.append("")
    lines.append("### Pilares da Preparação")
    lines.append("1. **Pareamento Semanal Fixo**: Duas disciplinas por dia com alternância de áreas correlatas e de suporte.")
    lines.append("2. **Ciclos Evolutivos (4 Ciclos)**: Transição progressiva de teoria e lei seca para simulados e caderno de erros.")
    lines.append("3. **Engenharia Reversa FGV**: Estudo orientado pelas pegadinhas de alternativas (distratores), posições minoritárias consagradas pela banca e jurisprudência vinculante.")
    lines.append("4. **Revisão Espaçada Cumulativa (D08+)**: A partir do 8º dia, 30% do tempo é compulsoriamente alocado para revisar conteúdos vistos com defasagem de 7, 3, 14 e 1 dias.")
    lines.append("")
    lines.append("## 2. Detalhamento dos 4 Ciclos")
    lines.append("")
    lines.append("### Ciclo 1: Semanas 1 a 4 (Sólida Inicialização - Dias 001 a 028)")
    lines.append("- Foco em leitura ativa da fonte normativa primária (Constituição, Códigos e Leis Especiais).")
    lines.append("- Elaboração de quadros sinópticos e tabelas comparativas curtas.")
    lines.append("- Resolução de baterias de questões FGV para decodificação do padrão estilístico da banca.")
    lines.append("")
    lines.append("### Ciclo 2: Semanas 5 a 8 (Avanço e Densidade - Dias 029 a 056)")
    lines.append("- Aprofundamento doutrinário pontual e leitura dirigida comparando institutos limítrofes.")
    lines.append("- Mapeamento minucioso de prazos processuais, exceções à regra geral e divergências sumuladas.")
    lines.append("- Engenharia reversa exaustiva de cada alternativa incorreta das questões FGV.")
    lines.append("")
    lines.append("### Ciclo 3: Semanas 9 a 12 (Legislação Local e Humanística - Dias 057 a 084)")
    lines.append("- Absorção intensiva do Código de Organização Judiciária e Regimento Interno do TJ-PE.")
    lines.append("- Noções Gerais de Direito e Formação Humanística (Sociologia, Psicologia, Filosofia, Ética e Teoria Geral).")
    lines.append("- Treinamento focado no mapa de pegadinhas normativas e jurisprudência de Direitos Humanos e Controle de Convencionalidade.")
    lines.append("")
    lines.append("### Ciclo 4: Semanas 13 a 17 (Simulados e Blindagem de Erros - Dias 085 a 108)")
    lines.append("- Realização de simulados setoriais e gerais cronometrados (condições reais de prova).")
    lines.append("- Auditoria severa e correção ativa do Caderno de Erros.")
    lines.append("- Revisão relâmpago por assertivas históricas da FGV e precedentes qualificados dos Tribunais Superiores (STF/STJ).")
    lines.append("")
    lines.append("## 3. Protocolo de Revisão e Espaçamento")
    lines.append("A curva de esquecimento é combatida através da rotação calculada:")
    lines.append("- **Offset 7**: revisão do que foi estudado há exatamente uma semana.")
    lines.append("- **Offset 3 e Offset 14**: consolidação de curto e médio prazo.")
    lines.append("- **Offset 1**: ancoragem imediata do dia anterior quando necessário.")
    lines.append("")
    return "\n".join(lines)

def generate_indice_md():
    lines = []
    lines.append("# Índice Geral e Estrutura do Acervo TJ-PE 2026")
    lines.append("")
    lines.append("Guia de navegação rápida e indexação de todos os arquivos do acervo de preparação para a Magistratura TJ-PE (Banca FGV).")
    lines.append("")
    lines.append("## Arquivos do Acervo")
    lines.append("")
    lines.append("1. `cronograma_tjpe_fgv.json`: Arquivo mestre de dados estruturados com metadados, ranking de disciplinas, matriz semanal e a régua completa de 108 dias.")
    lines.append("2. `cronograma_tjpe_fgv.md`: Documentação textual completa de 108 dias com divisão de carga diária, tópicos de estudo novo e planos de revisão.")
    lines.append("3. `mapeamento.json`: Definição estruturada em TypeScript das 14 disciplinas e seus subtemas estatísticos.")
    lines.append("4. `mapeamento_disciplinas_fgv.md`: Mapeamento estatístico verticalizado com todas as tabelas de incidência e curva de relevância temática.")
    lines.append("5. `generate_cronograma_tjpe_fgv.py`: Script gerador do algoritmo de distribuição de matérias, cálculo de prazos e pareamento de ciclos.")
    lines.append("6. `guia_metodologia_tjpe_fgv.md`: Metodologia de estudos em 4 ciclos, protocolos de engenharia reversa FGV e regras de revisão.")
    lines.append("")
    lines.append("## Instruções de Consulta via Custom PageIndex RAG")
    lines.append("- Utilize `search_documents` para localizar qualquer tema (ex: 'usucapião', 'litisconsórcio', 'prisão preventiva', 'dia 045', 'revisão').")
    lines.append("- Utilize `browse_documents` para navegar na árvore de documentos disponíveis.")
    lines.append("- Utilize `get_document_structure` para inspecionar os sumários e páginas de cada arquivo.")
    lines.append("- Utilize `get_page_content` para ler páginas ou intervalos específicos.")
    lines.append("")
    return "\n".join(lines)

def main():
    cron = load_cronograma()
    disciplines = load_mapeamento()
    
    cron_md = generate_cronograma_md(cron)
    (BASE_DIR / "cronograma_tjpe_fgv.md").write_text(cron_md, encoding="utf-8")
    print(f"Generated cronograma_tjpe_fgv.md: {len(cron_md)} chars")
    
    map_md = generate_mapeamento_md(disciplines)
    (BASE_DIR / "mapeamento_disciplinas_fgv.md").write_text(map_md, encoding="utf-8")
    print(f"Generated mapeamento_disciplinas_fgv.md: {len(map_md)} chars")
    
    guia_md = generate_guia_md(cron)
    (BASE_DIR / "guia_metodologia_tjpe_fgv.md").write_text(guia_md, encoding="utf-8")
    print(f"Generated guia_metodologia_tjpe_fgv.md: {len(guia_md)} chars")
    
    idx_md = generate_indice_md()
    (BASE_DIR / "indice_geral_tjpe_2026.md").write_text(idx_md, encoding="utf-8")
    print(f"Generated indice_geral_tjpe_2026.md: {len(idx_md)} chars")

if __name__ == "__main__":
    main()
