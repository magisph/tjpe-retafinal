import json
import re
from pathlib import Path

BASE_DIR = Path(r"c:\Users\Junior do Titico\Desktop\TJPE-2026")
MD_FILE = BASE_DIR / "cronograma_reta_final_tjpe_2026.md"
HTML_FILE = BASE_DIR / "cronograma_interativo_tjpe_2026.html"
INDEX_FILE = BASE_DIR / "index.html"

def parse_cronograma_md():
    content = MD_FILE.read_text(encoding="utf-8")
    
    # Divide por seções de dias: ### Dia X — DD/MM/AAAA ...
    day_blocks = re.split(r'\n###\s+(Dia\s+\d+\s+—\s+.+?\s+—\s+Fase\s+[IVX]+[^\n]*)', content)
    
    days = []
    # day_blocks[0] é o cabeçalho antes do primeiro dia
    for i in range(1, len(day_blocks), 2):
        header_line = day_blocks[i].strip()
        body = day_blocks[i+1] if i+1 < len(day_blocks) else ""
        
        # Ex: Dia 22 — 26/09/2026 (Sábado — Véspera da Prova) — Fase III: Blindagem de Véspera
        m_head = re.match(r'Dia\s+(\d+)\s+—\s+([0-9/]+)\s+\(([^)]+)\)\s+—\s+(Fase\s+[IVX]+):?\s*(.*)', header_line)
        if m_head:
            day_num = int(m_head.group(1))
            date_str = m_head.group(2)
            weekday_str = m_head.group(3)
            fase_code = m_head.group(4)
            fase_desc = m_head.group(5)
        else:
            day_num = len(days) + 1
            date_str = ""
            weekday_str = ""
            fase_code = "Fase I"
            fase_desc = ""

        # Extrair carga horária
        m_carga = re.search(r'-\s+\*\*Carga Horária Total\*\*:\s*(\d+)\s+horas?\s*\((\d+)\s+minutos?\)', body)
        total_hours = int(m_carga.group(1)) if m_carga else (6 if "Sábado" in weekday_str or "Domingo" in weekday_str else 4)
        total_mins = int(m_carga.group(2)) if m_carga else total_hours * 60

        # Extrair sessões 1, 2 e 3
        # Padrão: - **Sessão X (... — Y min)**:\n  - *Subtópicos*: ...\n  - *Método*: ...\n  - *Atividade*: ...
        sessions = []
        sess_pattern = re.compile(r'-\s+\*\*Sessão\s+(\d+)\s+\(([^)]+)\)\*\*:\s*\n((?:\s+-\s+\*(?:Subtópicos|Disciplina\(s\)|Método|Atividade)\*:.*\n?)+)')
        
        for sm in sess_pattern.finditer(body):
            s_num = int(sm.group(1))
            s_title_raw = sm.group(2)
            s_body = sm.group(3)
            
            # Divide título em disciplina e minutos
            # Ex: "Direito Administrativo — 140 min" ou "Treino Tático de Questões FGV — 100 min"
            parts = s_title_raw.split("—")
            disc_name = parts[0].strip()
            mins = 90
            if len(parts) > 1:
                m_m = re.search(r'(\d+)', parts[1])
                if m_m:
                    mins = int(m_m.group(1))
            
            # Subtópicos / Disciplinas
            m_sub = re.search(r'-\s+\*Subtópicos\*:\s*([^\n]+)', s_body)
            m_disc = re.search(r'-\s+\*Disciplina\(s\)\*:\s*([^\n]+)', s_body)
            if m_sub:
                subtopics = m_sub.group(1).strip()
            elif m_disc:
                subtopics = m_disc.group(1).strip()
            else:
                subtopics = ""
            
            # Método
            m_met = re.search(r'-\s+\*Método\*:\s*([^\n]+)', s_body)
            method = m_met.group(1).strip() if m_met else ""
            
            # Atividade
            m_atv = re.search(r'-\s+\*Atividade\*:\s*([^\n]+)', s_body)
            activity = m_atv.group(1).strip() if m_atv else ""
            
            sessions.append({
                "id": f"d{day_num}_s{s_num}",
                "sessionNum": s_num,
                "title": disc_name,
                "minutes": mins,
                "subtopics": subtopics,
                "method": method,
                "activity": activity
            })
            
        days.append({
            "dayNumber": day_num,
            "date": date_str,
            "weekday": weekday_str,
            "faseCode": fase_code,
            "faseTitle": f"{fase_code}: {fase_desc}".strip(),
            "totalHours": total_hours,
            "totalMinutes": total_mins,
            "sessions": sessions
        })
        
    return days

def generate_html(days_data):
    days_json_str = json.dumps(days_data, ensure_ascii=False)
    
    html_content = f"""<!DOCTYPE html>
<html lang="pt-BR" data-theme="light">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>TJ-PE 2026 | Cronograma Tático de Reta Final — Magistratura FGV</title>
  
  <!-- Progressive Web App (PWA) Manifest & Metatags -->
  <link rel="manifest" href="manifest.json">
  <meta name="theme-color" content="#0F2137">
  <meta name="mobile-web-app-capable" content="yes">
  <meta name="apple-mobile-web-app-capable" content="yes">
  <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
  <meta name="apple-mobile-web-app-title" content="TJPE 2026">
  <link rel="icon" type="image/png" sizes="32x32" href="icons/favicon-32.png">
  <link rel="icon" type="image/png" sizes="192x192" href="icons/icon-192.png">
  <link rel="apple-touch-icon" href="icons/icon-192.png">
  
  <!-- Fontes Tipográficas Oficiais do Design System -->
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&family=Newsreader:ital,opsz,wght@0,6..72,400;0,6..72,600;1,6..72,400&display=swap" rel="stylesheet">
  
  <!-- Chart.js via CDN para Visualizações Analíticas -->
  <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.1/dist/chart.umd.min.js"></script>

  <style>
    :root {{
      --font-sans: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
      --font-serif: 'Newsreader', Georgia, serif;
      --font-mono: 'JetBrains Mono', monospace;

      /* Paleta Tema Claro (Editorial Forense & High-Contrast) */
      --bg-canvas: #F8FAFC;
      --bg-surface: #FFFFFF;
      --bg-surface-elevated: #F1F5F9;
      --bg-surface-active: #E2E8F0;
      --border-subtle: #E2E8F0;
      --border-strong: #CBD5E1;
      
      --text-primary: #0F172A;
      --text-secondary: #475569;
      --text-muted: #64748B;
      --text-inverse: #FFFFFF;

      --primary-navy: #0F2137;
      --primary-accent: #1E3A8A;
      --judiciary-gold: #B45309;
      --gold-surface: #FEF3C7;
      
      --emerald-success: #059669;
      --emerald-surface: #ECFDF5;
      --emerald-border: #A7F3D0;
      
      --method-ls: #0369A1; /* Lei Seca Azul */
      --method-ls-bg: #E0F2FE;
      --method-j: #7C3AED;  /* Jurisprudência Roxo */
      --method-j-bg: #EDE9FE;
      --method-d: #B45309;  /* Doutrina Âmbar */
      --method-d-bg: #FEF3C7;
      
      --shadow-sm: 0 1px 2px 0 rgba(15, 23, 42, 0.05);
      --shadow-md: 0 4px 6px -1px rgba(15, 23, 42, 0.07), 0 2px 4px -2px rgba(15, 23, 42, 0.05);
      --shadow-lg: 0 10px 15px -3px rgba(15, 23, 42, 0.08), 0 4px 6px -4px rgba(15, 23, 42, 0.04);
      --radius-sm: 6px;
      --radius-md: 10px;
      --radius-lg: 14px;
      --radius-full: 9999px;
      
      --transition-fast: 0.15s ease;
      --transition-smooth: 0.25s cubic-bezier(0.16, 1, 0.3, 1);
    }}

    [data-theme="dark"] {{
      --bg-canvas: #090E17;
      --bg-surface: #111927;
      --bg-surface-elevated: #1A2436;
      --bg-surface-active: #243147;
      --border-subtle: #243147;
      --border-strong: #334155;
      
      --text-primary: #F8FAFC;
      --text-secondary: #94A3B8;
      --text-muted: #64748B;
      --text-inverse: #090E17;

      --primary-navy: #38BDF8;
      --primary-accent: #60A5FA;
      --judiciary-gold: #FBBF24;
      --gold-surface: #362808;
      
      --emerald-success: #10B981;
      --emerald-surface: #064E3B;
      --emerald-border: #047857;

      --method-ls: #38BDF8;
      --method-ls-bg: #0C4A6E;
      --method-j: #A78BFA;
      --method-j-bg: #4C1D95;
      --method-d: #FBBF24;
      --method-d-bg: #451A03;

      --shadow-sm: 0 1px 2px 0 rgba(0, 0, 0, 0.5);
      --shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.4);
      --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.5);
    }}

    /* Reset e Base */
    *, *::before, *::after {{
      box-sizing: border-box;
      margin: 0;
      padding: 0;
    }}

    body {{
      font-family: var(--font-sans);
      background-color: var(--bg-canvas);
      color: var(--text-primary);
      line-height: 1.6;
      -webkit-font-smoothing: antialiased;
      transition: background-color var(--transition-smooth), color var(--transition-smooth);
      padding-bottom: 5rem;
      overflow-x: hidden;
      width: 100%;
    }}

    /* Acessibilidade: Skip Link */
    .skip-link {{
      position: absolute;
      top: -40px;
      left: 1rem;
      background: var(--primary-accent);
      color: #FFF;
      padding: 0.5rem 1rem;
      border-radius: var(--radius-sm);
      z-index: 1000;
      transition: top 0.2s ease;
      text-decoration: none;
      font-weight: 600;
    }}
    .skip-link:focus {{
      top: 1rem;
      outline: 3px solid var(--judiciary-gold);
    }}

    /* Header Institucional Refinado e Minimalista */
    header.main-header {{
      background-color: var(--bg-surface);
      border-bottom: 1px solid var(--border-subtle);
      padding: 0.85rem 1.25rem;
      position: sticky;
      top: 0;
      z-index: 50;
      backdrop-filter: blur(12px);
      box-shadow: var(--shadow-sm);
    }}

    .header-container {{
      max-width: 1320px;
      margin: 0 auto;
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 0.75rem;
    }}

    .brand-group {{
      display: flex;
      align-items: center;
      gap: 0.85rem;
      min-width: 0;
    }}

    .brand-symbol {{
      width: 40px;
      height: 40px;
      flex-shrink: 0;
      background: linear-gradient(145deg, #09172B 0%, #13243E 100%);
      display: flex;
      align-items: center;
      justify-content: center;
      border-radius: 10px;
      border: 1px solid rgba(212, 175, 55, 0.4);
      box-shadow: 0 4px 10px rgba(11, 23, 43, 0.2), inset 0 1px 0 rgba(255, 255, 255, 0.12);
      transition: transform var(--transition-fast), border-color var(--transition-fast);
    }}

    .brand-symbol:hover {{
      transform: scale(1.04);
      border-color: rgba(212, 175, 55, 0.7);
    }}

    .brand-text {{
      display: flex;
      flex-direction: column;
      gap: 0.25rem;
      min-width: 0;
    }}

    .brand-title-row {{
      display: flex;
      align-items: center;
      gap: 0.5rem;
      flex-wrap: wrap;
    }}

    .brand-text h1 {{
      font-size: 1.1rem;
      font-weight: 800;
      color: var(--text-primary);
      letter-spacing: -0.02em;
      line-height: 1.2;
    }}

    .brand-meta-row {{
      display: flex;
      align-items: center;
      gap: 0.6rem;
      flex-wrap: wrap;
    }}

    .brand-subtitle {{
      font-size: 0.8rem;
      color: var(--text-muted);
      font-weight: 500;
      line-height: 1.2;
    }}

    .countdown-badge {{
      display: inline-flex;
      align-items: center;
      gap: 0.35rem;
      padding: 0;
      background: transparent;
      border: none;
      color: var(--text-secondary);
      font-weight: 600;
      font-size: 0.78rem;
      font-family: var(--font-mono);
      letter-spacing: -0.01em;
      white-space: nowrap;
    }}

    .header-actions {{
      display: flex;
      align-items: center;
      gap: 0.5rem;
      flex-shrink: 0;
    }}

    /* Botão de Tema Apenas com Ícone no Canto Superior Direito */
    .btn-icon-theme {{
      width: 40px;
      height: 40px;
      padding: 0;
      display: inline-flex;
      align-items: center;
      justify-content: center;
      border-radius: var(--radius-full);
      border: 1px solid var(--border-subtle);
      background-color: var(--bg-surface-elevated);
      color: var(--text-primary);
      font-size: 1.2rem;
      cursor: pointer;
      transition: all var(--transition-fast);
      outline: none;
    }}

    .btn-icon-theme:hover {{
      background-color: var(--bg-surface-active);
      border-color: var(--border-strong);
      transform: scale(1.06);
    }}

    .btn-icon-theme:focus-visible {{
      outline: 2px solid var(--primary-accent);
      outline-offset: 2px;
    }}

    .btn-install-badge {{
      display: inline-flex;
      align-items: center;
      gap: 0.35rem;
      padding: 0.45rem 0.75rem;
      font-size: 0.78rem;
      font-weight: 700;
      border-radius: var(--radius-full);
      border: 1px solid var(--judiciary-gold);
      background: var(--gold-surface);
      color: var(--judiciary-gold);
      cursor: pointer;
      transition: all var(--transition-fast);
    }}

    .btn-install-badge:hover {{
      filter: brightness(0.95);
      transform: translateY(-1px);
    }}

    /* Botão Discreto de Reset no Rodapé */
    .btn-footer-reset {{
      display: inline-flex;
      align-items: center;
      gap: 0.4rem;
      padding: 0.45rem 0.9rem;
      font-size: 0.78rem;
      font-weight: 600;
      color: var(--text-muted);
      background: var(--bg-surface);
      border: 1px solid var(--border-subtle);
      border-radius: var(--radius-md);
      cursor: pointer;
      transition: all var(--transition-fast);
    }}

    .btn-footer-reset:hover {{
      color: #EF4444;
      border-color: #FCA5A5;
      background: rgba(239, 68, 68, 0.05);
    }}

    @media (max-width: 640px) {{
      header.main-header {{
        padding: 0.65rem 0.85rem;
      }}
      .brand-symbol {{
        width: 36px;
        height: 36px;
        font-size: 1.1rem;
      }}
      .brand-text h1 {{
        font-size: 0.96rem;
      }}
      .brand-subtitle {{
        display: none;
      }}
      .countdown-badge {{
        font-size: 0.74rem;
        padding: 0;
      }}
      .btn-icon-theme {{
        width: 38px;
        height: 38px;
        font-size: 1.1rem;
      }}
      .install-text {{
        display: none;
      }}
      .btn-install-badge {{
        padding: 0.4rem 0.55rem;
      }}
      .metric-card {{
        padding: 0.5rem 0.6rem;
      }}
      .metric-title {{
        font-size: 0.58rem;
      }}
      .metric-value-large {{
        font-size: 1.12rem;
      }}
      .metric-detail {{
        font-size: 0.65rem;
      }}
      .day-card {{
        padding: 0.75rem 0.85rem;
      }}
      .day-title-text {{
        font-size: 0.95rem;
      }}
    }}

    .btn {{
      display: inline-flex;
      align-items: center;
      gap: 0.4rem;
      padding: 0.5rem 0.85rem;
      font-size: 0.82rem;
      font-weight: 600;
      border-radius: var(--radius-sm);
      border: 1px solid var(--border-subtle);
      background-color: var(--bg-surface-elevated);
      color: var(--text-primary);
      cursor: pointer;
      transition: all var(--transition-fast);
      text-decoration: none;
    }}

    .btn:hover {{
      background-color: var(--bg-surface-active);
      border-color: var(--border-strong);
    }}

    .btn:focus-visible {{
      outline: 2px solid var(--primary-accent);
      outline-offset: 2px;
    }}

    .btn-gold {{
      background: var(--gold-surface);
      color: var(--judiciary-gold);
      border-color: var(--judiciary-gold);
      font-weight: 700;
    }}

    /* Main Container */
    main.app-layout {{
      max-width: 1320px;
      margin: 1rem auto;
      padding: 0 1rem;
      display: grid;
      gap: 0.95rem;
      width: 100%;
      box-sizing: border-box;
      overflow-x: hidden;
    }}

    /* Dashboard Grid Compacto (4 colunas no Desktop, 2x2 no Mobile) */
    .dashboard-grid {{
      display: grid;
      grid-template-columns: repeat(4, 1fr);
      gap: 0.65rem;
      width: 100%;
      box-sizing: border-box;
    }}

    @media (max-width: 860px) {{
      .dashboard-grid {{
        grid-template-columns: repeat(2, 1fr);
        gap: 0.5rem;
      }}
    }}

    .metric-card {{
      background: var(--bg-surface);
      border: 1px solid var(--border-subtle);
      border-radius: var(--radius-md);
      padding: 0.65rem 0.85rem;
      box-shadow: var(--shadow-sm);
      display: flex;
      flex-direction: column;
      justify-content: space-between;
      position: relative;
      overflow: hidden;
      min-width: 0;
      box-sizing: border-box;
    }}

    .metric-card::before {{
      content: "";
      position: absolute;
      top: 0;
      left: 0;
      right: 0;
      height: 3px;
      background: var(--primary-accent);
    }}

    .metric-card.gold::before {{
      background: var(--judiciary-gold);
    }}

    .metric-card.emerald::before {{
      background: var(--emerald-success);
    }}

    .metric-header {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 0.15rem;
    }}

    .metric-title {{
      font-size: 0.66rem;
      font-weight: 700;
      text-transform: uppercase;
      letter-spacing: 0.04em;
      color: var(--text-muted);
    }}

    .metric-value-large {{
      font-size: 1.35rem;
      font-weight: 800;
      color: var(--text-primary);
      font-family: var(--font-mono);
      line-height: 1.1;
      margin: 0.1rem 0;
    }}

    .metric-detail {{
      font-size: 0.72rem;
      color: var(--text-secondary);
      font-weight: 500;
      line-height: 1.2;
    }}

    .progress-bar-container {{
      width: 100%;
      height: 5px;
      background-color: var(--bg-surface-elevated);
      border-radius: var(--radius-full);
      overflow: hidden;
      margin-top: 0.35rem;
    }}

    .progress-bar-fill {{
      height: 100%;
      background: linear-gradient(90deg, #1E3A8A 0%, #10B981 100%);
      border-radius: var(--radius-full);
      transition: width 0.4s ease;
    }}

    /* Sessão Gráfica Compacta */
    .analytics-panel {{
      background: var(--bg-surface);
      border: 1px solid var(--border-subtle);
      border-radius: var(--radius-md);
      padding: 0.75rem 1rem;
      box-shadow: var(--shadow-sm);
      display: grid;
      grid-template-columns: 1fr 1.6fr;
      gap: 1rem;
      align-items: center;
    }}

    @media (max-width: 860px) {{
      .analytics-panel {{
        grid-template-columns: 1fr;
        gap: 0.85rem;
        padding: 0.75rem;
      }}
    }}

    .chart-box {{
      position: relative;
      height: 145px;
      width: 100%;
    }}

    .chart-title {{
      font-size: 0.82rem;
      font-weight: 700;
      color: var(--text-primary);
      margin-bottom: 0.35rem;
    }}

    /* Barra de Controles e Filtros Compacta */
    .controls-bar {{
      background: var(--bg-surface);
      border: 1px solid var(--border-subtle);
      border-radius: var(--radius-md);
      padding: 0.45rem 0.75rem;
      display: flex;
      flex-wrap: wrap;
      align-items: center;
      justify-content: space-between;
      gap: 0.5rem;
      box-shadow: var(--shadow-sm);
      width: 100%;
      box-sizing: border-box;
    }}

    .filter-group {{
      display: flex;
      align-items: center;
      gap: 0.35rem;
      flex-wrap: wrap;
      min-width: 0;
    }}

    .filter-pill {{
      padding: 0.25rem 0.6rem;
      font-size: 0.72rem;
      font-weight: 600;
      border-radius: var(--radius-full);
      border: 1px solid var(--border-subtle);
      background: var(--bg-surface-elevated);
      color: var(--text-secondary);
      cursor: pointer;
      transition: all var(--transition-fast);
    }}

    .filter-pill:hover {{
      color: var(--text-primary);
      border-color: var(--border-strong);
    }}

    .filter-pill.active {{
      background: var(--primary-accent);
      color: #FFF;
      border-color: var(--primary-accent);
    }}

    .search-input-box {{
      position: relative;
      min-width: 180px;
      max-width: 260px;
      flex-grow: 1;
    }}

    @media (max-width: 640px) {{
      .search-input-box {{
        min-width: 100%;
        max-width: 100%;
      }}
    }}

    .search-input-box input {{
      width: 100%;
      padding: 0.32rem 0.65rem 0.32rem 1.85rem;
      font-size: 0.76rem;
      border-radius: var(--radius-sm);
      border: 1px solid var(--border-subtle);
      background: var(--bg-surface-elevated);
      color: var(--text-primary);
      font-family: inherit;
    }}

    .search-input-box input:focus {{
      outline: none;
      border-color: var(--primary-accent);
      background: var(--bg-surface);
      box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.15);
    }}

    .search-icon {{
      position: absolute;
      left: 0.6rem;
      top: 50%;
      transform: translateY(-50%);
      font-size: 0.78rem;
      color: var(--text-muted);
      pointer-events: none;
    }}

    /* Lista de Dias */
    .schedule-feed {{
      display: flex;
      flex-direction: column;
      gap: 0.85rem;
    }}

    .day-card {{
      background: var(--bg-surface);
      border: 1px solid var(--border-subtle);
      border-radius: var(--radius-md);
      padding: 0.85rem 1rem;
      box-shadow: var(--shadow-sm);
      transition: all var(--transition-smooth);
      position: relative;
    }}

    .day-card.completed {{
      border-color: var(--emerald-border);
      background: var(--emerald-surface);
    }}

    .day-badge-complete {{
      display: inline-flex;
      align-items: center;
      gap: 0.25rem;
      font-size: 0.72rem;
      font-weight: 800;
      color: var(--emerald-success);
      background: var(--bg-surface);
      padding: 0.2rem 0.6rem;
      border-radius: var(--radius-full);
      border: 1px solid var(--emerald-border);
      letter-spacing: 0.03em;
    }}

    .day-badge-partial {{
      display: inline-flex;
      align-items: center;
      font-size: 0.7rem;
      font-weight: 600;
      color: var(--text-muted);
      background: var(--bg-surface);
      padding: 0.15rem 0.45rem;
      border-radius: var(--radius-full);
      border: 1px solid var(--border-subtle);
      font-family: var(--font-mono);
    }}

    .day-header {{
      display: flex;
      flex-wrap: wrap;
      align-items: center;
      justify-content: space-between;
      gap: 0.5rem;
      padding-bottom: 0.85rem;
      border-bottom: 1px solid var(--border-subtle);
      margin-bottom: 1rem;
      width: 100%;
      box-sizing: border-box;
    }}

    .day-meta-left {{
      display: flex;
      align-items: center;
      gap: 0.5rem;
      flex-wrap: wrap;
      min-width: 0;
    }}

    .day-number-badge {{
      background: var(--primary-navy);
      color: #FFF;
      font-size: 0.85rem;
      font-weight: 800;
      font-family: var(--font-mono);
      padding: 0.35rem 0.75rem;
      border-radius: var(--radius-sm);
    }}

    .day-title-text {{
      font-size: 1.05rem;
      font-weight: 700;
      color: var(--text-primary);
    }}

    .day-tags {{
      display: flex;
      gap: 0.4rem;
      align-items: center;
      flex-wrap: wrap;
    }}

    .badge {{
      display: inline-flex;
      align-items: center;
      font-size: 0.72rem;
      font-weight: 700;
      padding: 0.2rem 0.55rem;
      border-radius: var(--radius-full);
      text-transform: uppercase;
      letter-spacing: 0.03em;
    }}

    .badge-fase1 {{ background: #E0E7FF; color: #3730A3; }}
    .badge-fase2 {{ background: #FEF3C7; color: #92400E; }}
    .badge-fase3 {{ background: #FCE7F3; color: #9D174D; }}
    .badge-hours {{ background: var(--bg-surface-elevated); color: var(--text-secondary); font-family: var(--font-mono); }}

    /* Sessões de Estudo */
    .sessions-container {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
      gap: 0.85rem;
      width: 100%;
      box-sizing: border-box;
    }}

    @media (max-width: 640px) {{
      .sessions-container {{
        grid-template-columns: 1fr;
      }}
    }}

    .session-item {{
      background: var(--bg-surface-elevated);
      border: 1px solid var(--border-subtle);
      border-radius: var(--radius-md);
      padding: 0.95rem;
      display: flex;
      flex-direction: column;
      justify-content: space-between;
      gap: 0.6rem;
      transition: all var(--transition-fast);
      cursor: pointer;
      position: relative;
    }}

    .session-item:hover {{
      border-color: var(--border-strong);
      transform: translateY(-1px);
    }}

    .session-item.done {{
      background: var(--bg-surface);
      border-color: var(--emerald-border);
      opacity: 0.88;
    }}

    .session-header {{
      display: flex;
      align-items: flex-start;
      gap: 0.65rem;
    }}

    .custom-checkbox {{
      margin-top: 0.2rem;
      width: 20px;
      height: 20px;
      accent-color: var(--emerald-success);
      cursor: pointer;
      flex-shrink: 0;
    }}

    .session-heading-group {{
      flex: 1;
    }}

    .session-title-line {{
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 0.5rem;
    }}

    .session-subject {{
      font-size: 0.9rem;
      font-weight: 700;
      color: var(--text-primary);
    }}

    .session-time {{
      font-size: 0.75rem;
      font-family: var(--font-mono);
      font-weight: 700;
      color: var(--text-muted);
      background: var(--bg-surface);
      padding: 0.15rem 0.45rem;
      border-radius: var(--radius-sm);
      border: 1px solid var(--border-subtle);
    }}

    .method-badge {{
      display: inline-block;
      font-size: 0.68rem;
      font-family: var(--font-mono);
      font-weight: 700;
      padding: 0.15rem 0.4rem;
      border-radius: var(--radius-sm);
      margin-top: 0.25rem;
    }}
    .method-badge.ls {{ background: var(--method-ls-bg); color: var(--method-ls); }}
    .method-badge.j {{ background: var(--method-j-bg); color: var(--method-j); }}
    .method-badge.d {{ background: var(--method-d-bg); color: var(--method-d); }}
    .method-badge.er {{ 
      background: rgba(168, 85, 247, 0.12); 
      color: #7E22CE; 
      border: 1px solid rgba(168, 85, 247, 0.28); 
    }}
    [data-theme="dark"] .method-badge.er {{
      background: rgba(192, 132, 252, 0.15); 
      color: #C084FC; 
      border-color: rgba(192, 132, 252, 0.35); 
    }}

    .tema-tag {{
      display: inline-flex;
      align-items: center;
      font-weight: 800;
      color: var(--primary-accent);
      background: var(--bg-surface-active);
      padding: 0.1rem 0.35rem;
      border-radius: 4px;
      font-size: 0.72rem;
      border: 1px solid var(--border-subtle);
      margin-right: 0.25rem;
      vertical-align: middle;
    }}

    .session-body {{
      font-size: 0.8rem;
      color: var(--text-secondary);
      line-height: 1.5;
    }}

    .session-temas-bullets {{
      list-style: disc outside;
      margin: 0.35rem 0 0.15rem 1.25rem;
      padding: 0;
    }}

    .session-temas-bullets li {{
      margin: 0.25rem 0;
      line-height: 1.45;
      color: var(--text-secondary);
      font-size: 0.8rem;
    }}

    .session-temas-bullets li::marker {{
      color: var(--judiciary-gold);
      font-size: 0.85em;
    }}

    /* Accordion de Atividade Prática Retrátil */
    .activity-accordion {{
      margin-top: 0.45rem;
      padding-top: 0.35rem;
      border-top: 1px dashed var(--border-subtle);
      font-size: 0.78rem;
    }}

    .activity-summary {{
      display: inline-flex;
      align-items: center;
      gap: 0.35rem;
      cursor: pointer;
      user-select: none;
      list-style: none;
      font-weight: 600;
      font-size: 0.75rem;
      color: var(--text-muted);
      transition: color var(--transition-fast);
      padding: 0.15rem 0;
    }}

    .activity-summary::-webkit-details-marker {{
      display: none;
    }}

    .activity-summary:hover {{
      color: var(--primary-accent);
    }}

    .activity-summary:focus-visible {{
      outline: 2px solid var(--primary-accent);
      outline-offset: 2px;
      border-radius: var(--radius-sm);
    }}

    .activity-toggle-icon {{
      display: inline-block;
      font-size: 0.95rem;
      font-weight: 700;
      line-height: 1;
      transform-origin: center;
      transition: transform var(--transition-fast);
      color: var(--text-muted);
    }}

    .activity-summary:hover .activity-toggle-icon {{
      color: var(--primary-accent);
    }}

    .activity-accordion[open] .activity-toggle-icon {{
      transform: rotate(90deg);
    }}

    .activity-content {{
      margin-top: 0.35rem;
      padding: 0.45rem 0.65rem;
      background: var(--bg-surface-elevated);
      border-radius: var(--radius-sm);
      border-left: 2px solid var(--judiciary-gold);
      color: var(--text-secondary);
      font-size: 0.76rem;
      line-height: 1.45;
      font-style: italic;
    }}

    .session-item.done .session-subject {{
      text-decoration: line-through;
      color: var(--text-muted);
    }}

    /* Rodapé */
    footer.main-footer {{
      margin-top: 3rem;
      border-top: 1px solid var(--border-subtle);
      padding: 2rem 1.5rem;
      text-align: center;
      font-size: 0.82rem;
      color: var(--text-muted);
    }}

    /* Modal de Backup */
    .modal-backdrop {{
      position: fixed;
      inset: 0;
      background: rgba(15, 23, 42, 0.6);
      backdrop-filter: blur(4px);
      z-index: 100;
      display: none;
      align-items: center;
      justify-content: center;
      padding: 1rem;
    }}

    .modal-backdrop.open {{
      display: flex;
    }}

    .modal-dialog {{
      background: var(--bg-surface);
      border: 1px solid var(--border-subtle);
      border-radius: var(--radius-lg);
      padding: 1.5rem;
      max-width: 480px;
      width: 100%;
      box-shadow: var(--shadow-lg);
    }}

    .modal-header {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 1rem;
    }}

    .modal-title {{
      font-size: 1.1rem;
      font-weight: 700;
    }}

    .modal-body {{
      font-size: 0.85rem;
      color: var(--text-secondary);
      margin-bottom: 1.5rem;
      line-height: 1.6;
    }}

    .modal-actions {{
      display: flex;
      justify-content: flex-end;
      gap: 0.75rem;
    }}

    /* Impressão Limpa */
    @media print {{
      header.main-header, .controls-bar, .analytics-panel, .header-actions {{
        display: none !important;
      }}
      body {{
        background: #FFF !important;
        color: #000 !important;
      }}
      .day-card {{
        break-inside: avoid;
        border: 1px solid #CCC !important;
        box-shadow: none !important;
        margin-bottom: 1.5rem;
      }}
      .session-item {{
        background: #FFF !important;
        border: 1px solid #DDD !important;
      }}
    }}
  </style>
</head>
<body>
  <a href="#main-content" class="skip-link">Pular para o conteúdo principal</a>

  <!-- Cabeçalho -->
  <header class="main-header" role="banner">
    <div class="header-container">
      <div class="brand-group">
        <div class="brand-symbol" aria-hidden="true" title="TJ-PE · Magistratura Estadual">
          <svg width="22" height="22" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <defs>
              <linearGradient id="goldScales" x1="2" y1="2" x2="22" y2="22" gradientUnits="userSpaceOnUse">
                <stop stop-color="#FDE68A"/>
                <stop offset="0.6" stop-color="#E5A93C"/>
                <stop offset="1" stop-color="#B8860B"/>
              </linearGradient>
            </defs>
            <line x1="12" y1="3" x2="12" y2="20.5" stroke="url(#goldScales)" stroke-width="1.8" stroke-linecap="round"/>
            <circle cx="12" cy="3" r="1.3" fill="#FDE68A"/>
            <line x1="4" y1="7" x2="20" y2="7" stroke="url(#goldScales)" stroke-width="1.8" stroke-linecap="round"/>
            <line x1="4.5" y1="7" x2="2.2" y2="12" stroke="url(#goldScales)" stroke-width="1.2" stroke-linecap="round"/>
            <line x1="4.5" y1="7" x2="6.8" y2="12" stroke="url(#goldScales)" stroke-width="1.2" stroke-linecap="round"/>
            <line x1="19.5" y1="7" x2="17.2" y2="12" stroke="url(#goldScales)" stroke-width="1.2" stroke-linecap="round"/>
            <line x1="19.5" y1="7" x2="21.8" y2="12" stroke="url(#goldScales)" stroke-width="1.2" stroke-linecap="round"/>
            <path d="M1.8 12.2C1.8 13.9 3 15.2 4.5 15.2C6 15.2 7.2 13.9 7.2 12.2H1.8Z" fill="url(#goldScales)" fill-opacity="0.25" stroke="url(#goldScales)" stroke-width="1.2" stroke-linejoin="round"/>
            <path d="M16.8 12.2C16.8 13.9 18 15.2 19.5 15.2C21 15.2 22.2 13.9 22.2 12.2H16.8Z" fill="url(#goldScales)" fill-opacity="0.25" stroke="url(#goldScales)" stroke-width="1.2" stroke-linejoin="round"/>
            <line x1="8" y1="20.5" x2="16" y2="20.5" stroke="url(#goldScales)" stroke-width="2" stroke-linecap="round"/>
          </svg>
        </div>
        <div class="brand-text">
          <div class="brand-title-row">
            <h1>TJ-PE 2026 · Magistratura Estadual</h1>
          </div>
          <div class="brand-meta-row">
            <span class="brand-subtitle">Plano Tático de Reta Final (FGV)</span>
            <div class="countdown-badge" id="countdown-display" title="Data da Prova: 27 de Setembro de 2026">
              <span>📅</span> <span id="countdown-text">Calculando...</span>
            </div>
          </div>
        </div>
      </div>

      <div class="header-actions">
        <button class="btn-install-badge" id="btn-install-pwa" style="display: none;" title="Instalar aplicativo no seu dispositivo">
          <span>📲</span> <span class="install-text">Instalar App</span>
        </button>
        <button class="btn-icon-theme" id="btn-theme-toggle" aria-label="Alternar Tema Claro e Escuro" title="Alternar Tema">
          <span id="theme-icon">🌙</span>
        </button>
      </div>
    </div>
  </header>

  <!-- Conteúdo Principal -->
  <main class="app-layout" id="main-content" role="main">
    
    <!-- Painel de Métricas -->
    <section class="dashboard-grid" aria-label="Métricas Consolidadas de Progresso">
      <div class="metric-card gold">
        <div class="metric-header">
          <span class="metric-title">Progresso Global</span>
          <span style="font-size: 1.1rem;">🎯</span>
        </div>
        <div class="metric-value-large" id="metric-percent">0%</div>
        <div class="metric-detail" id="metric-ratio">0 de 66 sessões concluídas</div>
        <div class="progress-bar-container">
          <div class="progress-bar-fill" id="metric-progress-fill" style="width: 0%;"></div>
        </div>
      </div>

      <div class="metric-card">
        <div class="metric-header">
          <span class="metric-title">Carga Horária Estudada</span>
          <span style="font-size: 1.1rem;">⏱️</span>
        </div>
        <div class="metric-value-large" id="metric-hours">0h / 102h</div>
        <div class="metric-detail" id="metric-hours-pct">Faltam 102.0 horas líquidas</div>
      </div>

      <div class="metric-card emerald">
        <div class="metric-header">
          <span class="metric-title">Dias 100% Cumpridos</span>
          <span style="font-size: 1.1rem;">📆</span>
        </div>
        <div class="metric-value-large" id="metric-days">0 / 22</div>
        <div class="metric-detail" id="metric-days-pct">0% da régua de 22 dias</div>
      </div>

      <div class="metric-card">
        <div class="metric-header">
          <span class="metric-title">Questões FGV Realizadas</span>
          <span style="font-size: 1.1rem;">📝</span>
        </div>
        <div class="metric-value-large" id="metric-questions">0 / 460+</div>
        <div class="metric-detail">Engenharia reversa em cada sessão</div>
      </div>
    </section>

    <!-- Painel Analítico com Gráfico Compacto -->
    <section class="analytics-panel" aria-label="Gráficos de Acompanhamento">
      <div>
        <h2 class="chart-title">Distribuição Geral de Progresso</h2>
        <div class="chart-box">
          <canvas id="progressDoughnutChart"></canvas>
        </div>
      </div>

      <div>
        <h2 class="chart-title">Carga Horária Estudada por Fase (Horas)</h2>
        <div class="chart-box">
          <canvas id="phasesBarChart"></canvas>
        </div>
      </div>
    </section>

    <!-- Controles e Filtros -->
    <section class="controls-bar" aria-label="Filtros e Busca">
      <div class="filter-group" role="tablist" aria-label="Filtrar por Fase">
        <button class="filter-pill active" data-filter="all" role="tab" aria-selected="true">Todos os 22 Dias</button>
        <button class="filter-pill" data-filter="Fase I" role="tab" aria-selected="false">Fase I (D1 a D10)</button>
        <button class="filter-pill" data-filter="Fase II" role="tab" aria-selected="false">Fase II (D11 a D18)</button>
        <button class="filter-pill" data-filter="Fase III" role="tab" aria-selected="false">Fase III (D19 a D22)</button>
      </div>

      <div class="filter-group">
        <button class="filter-pill" data-status="pending">Pendentes</button>
        <button class="filter-pill" data-status="completed">Concluídos</button>
      </div>

      <div class="search-input-box">
        <span class="search-icon">🔍</span>
        <input type="text" id="search-input" placeholder="Buscar por tema ou disciplina..." aria-label="Buscar por tema ou disciplina">
      </div>
    </section>

    <!-- Lista dos Dias do Cronograma -->
    <section class="schedule-feed" id="schedule-container" aria-label="Cronograma Dia a Dia">
      <!-- Inserido dinamicamente via JS -->
    </section>

  </main>

  <!-- Rodapé -->
  <footer class="main-footer" role="contentinfo">
    <p><strong>TJ-PE 2026 · Cronograma de Reta Final para Magistratura Estadual</strong></p>
    <p style="margin-top: 0.25rem;">Planejamento tático orientado pelo banco de dados de 1.800 questões históricas da Banca FGV.</p>
    <div style="margin-top: 1.25rem;">
      <button class="btn-footer-reset" id="btn-reset" title="Reiniciar todo o progresso de estudos">
        <span>↺</span> Reiniciar Progresso
      </button>
    </div>
  </footer>

  <!-- Modal de Confirmação de Reset -->
  <div class="modal-backdrop" id="reset-modal" role="dialog" aria-modal="true" aria-labelledby="modal-title">
    <div class="modal-dialog">
      <div class="modal-header">
        <h3 class="modal-title" id="modal-title">Reiniciar Todo o Progresso?</h3>
      </div>
      <div class="modal-body">
        Esta ação desmarcará todas as sessões concluídas e redefinirá os gráficos para 0%. Esta operação não pode ser desfeita, a menos que você tenha feito um backup exportado.
      </div>
      <div class="modal-actions">
        <button class="btn" id="btn-cancel-reset">Cancelar</button>
        <button class="btn btn-gold" id="btn-confirm-reset">Sim, Reiniciar</button>
      </div>
    </div>
  </div>

  <script>
    // Registro do Service Worker para suporte a PWA e funcionamento offline
    if ('serviceWorker' in navigator) {{
      window.addEventListener('load', () => {{
        navigator.serviceWorker.register('./sw.js')
          .then(reg => console.log('[PWA] ServiceWorker registrado com sucesso:', reg.scope))
          .catch(err => console.warn('[PWA] Falha ao registrar ServiceWorker:', err));
      }});
    }}

    // Gerenciamento de Instalação PWA no Android / Chrome
    let deferredPrompt = null;
    window.addEventListener('beforeinstallprompt', (e) => {{
      e.preventDefault();
      deferredPrompt = e;
      const btnInstall = document.getElementById('btn-install-pwa');
      if (btnInstall) {{
        btnInstall.style.display = 'inline-flex';
      }}
    }});

    window.addEventListener('appinstalled', () => {{
      deferredPrompt = null;
      const btnInstall = document.getElementById('btn-install-pwa');
      if (btnInstall) {{
        btnInstall.style.display = 'none';
      }}
      console.log('[PWA] Aplicativo instalado com sucesso na tela inicial!');
    }});

    // Base de dados completa dos 22 dias extraída do cronograma
    const SCHEDULE_DATA = {days_json_str};

    // Estado da Aplicação e Persistência em LocalStorage
    const STORAGE_KEY = "tjpe_2026_study_progress";
    let completedSessions = new Set();
    let currentFilterFase = "all";
    let currentFilterStatus = "all";
    let currentSearchTerm = "";

    // Instâncias do Chart.js
    let doughnutChart = null;
    let barChart = null;

    // Inicialização
    function initApp() {{
      loadProgress();
      setupTheme();
      initCountdown();
      initCharts();
      renderSchedule();
      updateMetrics();
      setupEventListeners();
    }}

    // Carregar progresso do LocalStorage
    function loadProgress() {{
      try {{
        const raw = localStorage.getItem(STORAGE_KEY);
        if (raw) {{
          const arr = JSON.parse(raw);
          if (Array.isArray(arr)) {{
            completedSessions = new Set(arr);
          }}
        }}
      }} catch (e) {{
        console.error("Erro ao carregar do localStorage:", e);
      }}
    }}

    // Salvar progresso
    function saveProgress() {{
      try {{
        localStorage.setItem(STORAGE_KEY, JSON.stringify(Array.from(completedSessions)));
      }} catch (e) {{
        console.error("Erro ao salvar no localStorage:", e);
      }}
    }}

    // Configuração de Tema Claro / Escuro
    function setupTheme() {{
      const savedTheme = localStorage.getItem("tjpe_theme") || "light";
      document.documentElement.setAttribute("data-theme", savedTheme);
      updateThemeButton(savedTheme);
    }}

    function updateThemeButton(theme) {{
      const icon = document.getElementById("theme-icon");
      const btn = document.getElementById("btn-theme-toggle");
      if (theme === "dark") {{
        if (icon) icon.textContent = "☀️";
        if (btn) btn.setAttribute("title", "Alternar para Tema Claro");
        if (btn) btn.setAttribute("aria-label", "Alternar para Tema Claro");
      }} else {{
        if (icon) icon.textContent = "🌙";
        if (btn) btn.setAttribute("title", "Alternar para Tema Escuro");
        if (btn) btn.setAttribute("aria-label", "Alternar para Tema Escuro");
      }}
    }}

    function toggleTheme() {{
      const current = document.documentElement.getAttribute("data-theme") || "light";
      const next = current === "light" ? "dark" : "light";
      document.documentElement.setAttribute("data-theme", next);
      localStorage.setItem("tjpe_theme", next);
      updateThemeButton(next);
      updateChartsTheme();
    }}

    // Contagem Regressiva para a Prova (27/09/2026)
    function initCountdown() {{
      const examDate = new Date(2026, 8, 27, 8, 0, 0); // 27/09/2026
      const now = new Date();
      const diffMs = examDate - now;
      const diffDays = Math.ceil(diffMs / (1000 * 60 * 60 * 24));
      
      const el = document.getElementById("countdown-text");
      if (diffDays > 0) {{
        el.textContent = `Prova em ${{diffDays}} dias (27/09/2026)`;
      }} else if (diffDays === 0) {{
        el.textContent = "É HOJE! Boa Prova!";
      }} else {{
        el.textContent = "Prova Realizada em 27/09/2026";
      }}
    }}

    // Renderização do Cronograma
    function renderSchedule() {{
      const container = document.getElementById("schedule-container");
      container.innerHTML = "";

      let visibleCount = 0;

      SCHEDULE_DATA.forEach(day => {{
        // Filtro por Fase
        if (currentFilterFase !== "all" && !day.faseCode.startsWith(currentFilterFase)) {{
          return;
        }}

        // Verificar sessões concluídas do dia
        const totalDaySessions = day.sessions.length;
        const doneDaySessions = day.sessions.filter(s => completedSessions.has(s.id)).length;
        const isDayComplete = totalDaySessions > 0 && doneDaySessions === totalDaySessions;

        // Filtro por Status
        if (currentFilterStatus === "completed" && !isDayComplete) {{
          return;
        }}
        if (currentFilterStatus === "pending" && isDayComplete) {{
          return;
        }}

        // Filtro por Busca de Texto
        if (currentSearchTerm) {{
          const term = currentSearchTerm.toLowerCase();
          const matchDay = day.weekday.toLowerCase().includes(term) || day.date.includes(term);
          const matchSessions = day.sessions.some(s => 
            s.title.toLowerCase().includes(term) || 
            s.subtopics.toLowerCase().includes(term) || 
            s.activity.toLowerCase().includes(term)
          );
          if (!matchDay && !matchSessions) {{
            return;
          }}
        }}

        visibleCount++;

        // Determinar badge da Fase
        let faseBadgeClass = "badge-fase1";
        if (day.faseCode.includes("II")) faseBadgeClass = "badge-fase2";
        if (day.faseCode.includes("III")) faseBadgeClass = "badge-fase3";

        const card = document.createElement("article");
        card.className = `day-card ${{isDayComplete ? "completed" : ""}}`;
        card.id = `day-card-${{day.dayNumber}}`;

        let statusBadge = "";
        if (isDayComplete) {{
          statusBadge = '<span class="day-badge-complete">✓ Dia Cumprido</span>';
        }} else if (doneDaySessions > 0) {{
          statusBadge = `<span class="day-badge-partial">${{doneDaySessions}}/${{totalDaySessions}} sessões</span>`;
        }}

        card.innerHTML = `
          <div class="day-header">
            <div class="day-meta-left">
              <span class="day-number-badge">DIA ${{String(day.dayNumber).padStart(2, '0')}}</span>
              <span class="day-title-text">${{day.date}} (${{day.weekday}})</span>
              <div class="day-tags">
                <span class="badge ${{faseBadgeClass}}">${{day.faseCode}}</span>
                <span class="badge badge-hours">${{day.totalHours}}h (${{day.totalMinutes}} min)</span>
              </div>
            </div>
            <div class="day-meta-right">
              ${{statusBadge}}
            </div>
          </div>

          <div class="sessions-container">
            ${{day.sessions.map(session => {{
              const isDone = completedSessions.has(session.id);
              
              // Extração de tags de método ([LS], [J], [D], [ER])
              let methodBadges = "";
              if (session.method.includes("[LS]")) methodBadges += '<span class="method-badge ls">[LS] Lei Seca</span> ';
              if (session.method.includes("[J]")) methodBadges += '<span class="method-badge j">[J] Jurisprudência</span> ';
              if (session.method.includes("[D]")) methodBadges += '<span class="method-badge d">[D] Doutrina</span> ';
              if (session.method.includes("[ER]")) methodBadges += '<span class="method-badge er">[ER] Estudo Reverso FGV</span> ';
              if (!methodBadges) methodBadges = `<span class="method-badge">${{session.method}}</span>`;

              // Formatação de Tópicos (Múltiplos temas vs Tópicos normais)
              let topicsHtml = "";
              const temaRegex = /(?:\\*\\*)?Tema A(?:\\*\\*)?:?\\s*(.*?)\\s*\\|\\s*(?:\\*\\*)?Tema B(?:\\*\\*)?:?\\s*(.*)/;
              const temaMatch = session.subtopics ? session.subtopics.match(temaRegex) : null;

              if (temaMatch) {{
                const temaA = temaMatch[1].trim();
                const temaB = temaMatch[2].trim();
                topicsHtml = `
                  <strong>Tópicos:</strong>
                  <ul class="session-temas-bullets">
                    <li><span class="tema-tag">Tema A</span> <span>${{temaA}}</span></li>
                    <li><span class="tema-tag">Tema B</span> <span>${{temaB}}</span></li>
                  </ul>
                `;
              }} else {{
                let formattedSubtopics = (session.subtopics || "")
                  .replace(/\\*\\*(Tema [AB])\\*\\*:\\s*/g, '<span class="tema-tag">$1</span> ')
                  .replace(/\\*\\*(Tema [AB])\\*\\*/g, '<span class="tema-tag">$1</span>');
                topicsHtml = `<strong>Tópicos:</strong> ${{formattedSubtopics}}`;
              }}

              return `
                <div class="session-item ${{isDone ? 'done' : ''}}" onclick="toggleSessionClick(event, '${{session.id}}')">
                  <div class="session-header">
                    <input type="checkbox" class="custom-checkbox" 
                           id="chk-${{session.id}}" 
                           ${{isDone ? 'checked' : ''}} 
                           aria-label="Marcar ${{session.title}} como concluído"
                           onclick="event.stopPropagation(); toggleSession('${{session.id}}');">
                    <div class="session-heading-group">
                      <div class="session-title-line">
                        <span class="session-subject">Sessão ${{session.sessionNum}}: ${{session.title}}</span>
                        <span class="session-time">${{session.minutes}} min</span>
                      </div>
                      <div>${{methodBadges}}</div>
                    </div>
                  </div>
                  <div class="session-body">
                    ${{topicsHtml}}
                  </div>
                  <details class="activity-accordion" onclick="event.stopPropagation();">
                    <summary class="activity-summary">
                      <span class="activity-toggle-icon">›</span>
                      <span class="activity-summary-text">Atividade Prática</span>
                    </summary>
                    <div class="activity-content">
                      ${{session.activity}}
                    </div>
                  </details>
                </div>
              `;
            }}).join("")}}
          </div>
        `;

        container.appendChild(card);
      }});

      if (visibleCount === 0) {{
        container.innerHTML = `
          <div style="text-align: center; padding: 3rem; background: var(--bg-surface); border-radius: var(--radius-lg); border: 1px dashed var(--border-strong);">
            <div style="font-size: 2rem; margin-bottom: 0.5rem;">🔍</div>
            <h3 style="font-size: 1.1rem; font-weight: 700;">Nenhum dia localizado</h3>
            <p style="font-size: 0.85rem; color: var(--text-muted); margin-top: 0.25rem;">Tente ajustar os filtros ou o termo de busca.</p>
          </div>
        `;
      }}
    }}

    // Alternar sessão individual
    function toggleSession(sessionId) {{
      if (completedSessions.has(sessionId)) {{
        completedSessions.delete(sessionId);
      }} else {{
        completedSessions.add(sessionId);
      }}
      saveProgress();
      renderSchedule();
      updateMetrics();
      updateCharts();
    }}

    function toggleSessionClick(e, sessionId) {{
      // Não reprocessar se o clique veio do próprio input checkbox ou do accordion de atividade
      if (e.target && (e.target.type === 'checkbox' || e.target.closest('details') || e.target.closest('.activity-accordion'))) return;
      toggleSession(sessionId);
    }}

    // Alternar todas as sessões do dia
    function toggleAllDaySessions(dayNumber) {{
      const day = SCHEDULE_DATA.find(d => d.dayNumber === dayNumber);
      if (!day) return;

      const allDone = day.sessions.every(s => completedSessions.has(s.id));
      day.sessions.forEach(s => {{
        if (allDone) {{
          completedSessions.delete(s.id);
        }} else {{
          completedSessions.add(s.id);
        }}
      }});

      saveProgress();
      renderSchedule();
      updateMetrics();
      updateCharts();
    }}

    // Atualização de Métricas
    function updateMetrics() {{
      const totalSessions = 66; // 22 dias * 3 sessões
      const completedCount = completedSessions.size;
      const pct = Math.round((completedCount / totalSessions) * 100);

      // Horas
      let completedMins = 0;
      let totalMins = 0;
      let completedDays = 0;

      SCHEDULE_DATA.forEach(d => {{
        totalMins += d.totalMinutes;
        const allDayDone = d.sessions.length > 0 && d.sessions.every(s => completedSessions.has(s.id));
        if (allDayDone) completedDays++;

        d.sessions.forEach(s => {{
          if (completedSessions.has(s.id)) {{
            completedMins += s.minutes;
          }}
        }});
      }});

      const completedHours = (completedMins / 60).toFixed(1);
      const totalHours = (totalMins / 60).toFixed(1);
      const remainingHours = ((totalMins - completedMins) / 60).toFixed(1);

      document.getElementById("metric-percent").textContent = `${{pct}}%`;
      document.getElementById("metric-ratio").textContent = `${{completedCount}} de ${{totalSessions}} sessões concluídas`;
      document.getElementById("metric-progress-fill").style.width = `${{pct}}%`;

      document.getElementById("metric-hours").textContent = `${{completedHours}}h / ${{totalHours}}h`;
      document.getElementById("metric-hours-pct").textContent = `Faltam ${{remainingHours}} horas líquidas`;

      document.getElementById("metric-days").textContent = `${{completedDays}} / 22`;
      document.getElementById("metric-days-pct").textContent = `${{Math.round((completedDays/22)*100)}}% da régua de 22 dias`;

      // Estimativa de questões (média de 21 questões por sessão 3 realizada)
      const qSessionsDone = Array.from(completedSessions).filter(id => id.endsWith("_s3")).length;
      const estimatedQuestions = qSessionsDone * 21;
      document.getElementById("metric-questions").textContent = `${{estimatedQuestions}} / 460+`;
    }}

    // Inicialização dos Gráficos Chart.js
    function initCharts() {{
      const isDark = document.documentElement.getAttribute("data-theme") === "dark";
      const textColor = isDark ? "#94A3B8" : "#475569";
      const gridColor = isDark ? "#243147" : "#E2E8F0";

      // 1. Donut Chart de Conclusão Global
      const ctxDoughnut = document.getElementById("progressDoughnutChart").getContext("2d");
      doughnutChart = new Chart(ctxDoughnut, {{
        type: "doughnut",
        data: {{
          labels: ["Concluído", "Pendente"],
          datasets: [{{
            data: [0, 66],
            backgroundColor: ["#10B981", isDark ? "#1E293B" : "#E2E8F0"],
            borderColor: isDark ? "#111927" : "#FFFFFF",
            borderWidth: 2,
            hoverOffset: 4
          }}]
        }},
        options: {{
          responsive: true,
          maintainAspectRatio: false,
          cutout: "75%",
          plugins: {{
            legend: {{
              position: "bottom",
              labels: {{ color: textColor, font: {{ family: "'Plus Jakarta Sans', sans-serif", size: 11 }} }}
            }},
            tooltip: {{
              callbacks: {{
                label: function(context) {{
                  const label = context.label || "";
                  const val = context.raw || 0;
                  const pct = Math.round((val / 66) * 100);
                  return `${{label}}: ${{val}} sessões (${{pct}}%)`;
                }}
              }}
            }}
          }}
        }}
      }});

      // 2. Bar Chart de Horas por Fase
      const ctxBar = document.getElementById("phasesBarChart").getContext("2d");
      barChart = new Chart(ctxBar, {{
        type: "bar",
        data: {{
          labels: ["Fase I (D1-10)", "Fase II (D11-18)", "Fase III (D19-22)"],
          datasets: [
            {{
              label: "Horas Cumpridas",
              data: [0, 0, 0],
              backgroundColor: "#10B981",
              borderRadius: 4
            }},
            {{
              label: "Horas Pendentes",
              data: [48, 36, 18],
              backgroundColor: isDark ? "#1E293B" : "#CBD5E1",
              borderRadius: 4
            }}
          ]
        }},
        options: {{
          responsive: true,
          maintainAspectRatio: false,
          scales: {{
            x: {{
              stacked: true,
              grid: {{ display: false }},
              ticks: {{ color: textColor, font: {{ family: "'Plus Jakarta Sans', sans-serif", size: 11 }} }}
            }},
            y: {{
              stacked: true,
              grid: {{ color: gridColor }},
              ticks: {{ color: textColor, font: {{ family: "'Plus Jakarta Sans', sans-serif", size: 11 }} }},
              title: {{ display: true, text: "Horas Líquidas", color: textColor, font: {{ size: 11, weight: 600 }} }}
            }}
          }},
          plugins: {{
            legend: {{
              position: "bottom",
              labels: {{ color: textColor, font: {{ family: "'Plus Jakarta Sans', sans-serif", size: 11 }} }}
            }}
          }}
        }}
      }});

      updateCharts();
    }}

    function updateCharts() {{
      if (!doughnutChart || !barChart) return;

      const doneCount = completedSessions.size;
      const pendingCount = 66 - doneCount;

      doughnutChart.data.datasets[0].data = [doneCount, pendingCount];
      doughnutChart.update();

      // Calcular horas por fase
      let fase1DoneMins = 0, fase1TotalMins = 0;
      let fase2DoneMins = 0, fase2TotalMins = 0;
      let fase3DoneMins = 0, fase3TotalMins = 0;

      SCHEDULE_DATA.forEach(d => {{
        const isF1 = d.faseCode.includes("Fase I");
        const isF2 = d.faseCode.includes("Fase II");
        const isF3 = d.faseCode.includes("Fase III");

        d.sessions.forEach(s => {{
          if (isF1) {{
            fase1TotalMins += s.minutes;
            if (completedSessions.has(s.id)) fase1DoneMins += s.minutes;
          }} else if (isF2) {{
            fase2TotalMins += s.minutes;
            if (completedSessions.has(s.id)) fase2DoneMins += s.minutes;
          }} else if (isF3) {{
            fase3TotalMins += s.minutes;
            if (completedSessions.has(s.id)) fase3DoneMins += s.minutes;
          }}
        }});
      }});

      const f1DoneH = +(fase1DoneMins / 60).toFixed(1);
      const f1PendH = +((fase1TotalMins - fase1DoneMins) / 60).toFixed(1);

      const f2DoneH = +(fase2DoneMins / 60).toFixed(1);
      const f2PendH = +((fase2TotalMins - fase2DoneMins) / 60).toFixed(1);

      const f3DoneH = +(fase3DoneMins / 60).toFixed(1);
      const f3PendH = +((fase3TotalMins - fase3DoneMins) / 60).toFixed(1);

      barChart.data.datasets[0].data = [f1DoneH, f2DoneH, f3DoneH];
      barChart.data.datasets[1].data = [f1PendH, f2PendH, f3PendH];
      barChart.update();
    }}

    function updateChartsTheme() {{
      const isDark = document.documentElement.getAttribute("data-theme") === "dark";
      const textColor = isDark ? "#94A3B8" : "#475569";
      const gridColor = isDark ? "#243147" : "#E2E8F0";

      if (doughnutChart) {{
        doughnutChart.data.datasets[0].backgroundColor[1] = isDark ? "#1E293B" : "#E2E8F0";
        doughnutChart.data.datasets[0].borderColor = isDark ? "#111927" : "#FFFFFF";
        doughnutChart.options.plugins.legend.labels.color = textColor;
        doughnutChart.update();
      }}

      if (barChart) {{
        barChart.data.datasets[1].backgroundColor = isDark ? "#1E293B" : "#CBD5E1";
        barChart.options.scales.x.ticks.color = textColor;
        barChart.options.scales.y.ticks.color = textColor;
        barChart.options.scales.y.grid.color = gridColor;
        barChart.options.scales.y.title.color = textColor;
        barChart.options.plugins.legend.labels.color = textColor;
        barChart.update();
      }}
    }}

    // Configuração dos Event Listeners
    function setupEventListeners() {{
      // Tema
      document.getElementById("btn-theme-toggle").addEventListener("click", toggleTheme);

      // Filtros de Fase
      document.querySelectorAll("[data-filter]").forEach(btn => {{
        btn.addEventListener("click", function() {{
          document.querySelectorAll("[data-filter]").forEach(b => b.classList.remove("active"));
          this.classList.add("active");
          currentFilterFase = this.getAttribute("data-filter");
          renderSchedule();
        }});
      }});

      // Filtros de Status
      document.querySelectorAll("[data-status]").forEach(btn => {{
        btn.addEventListener("click", function() {{
          const isSelected = this.classList.contains("active");
          document.querySelectorAll("[data-status]").forEach(b => b.classList.remove("active"));
          if (!isSelected) {{
            this.classList.add("active");
            currentFilterStatus = this.getAttribute("data-status");
          }} else {{
            currentFilterStatus = "all";
          }}
          renderSchedule();
        }});
      }});

      // Campo de Busca
      const searchInput = document.getElementById("search-input");
      searchInput.addEventListener("input", function(e) {{
        currentSearchTerm = e.target.value.trim();
        renderSchedule();
      }});

      // Reset Modal
      const modal = document.getElementById("reset-modal");
      document.getElementById("btn-reset").addEventListener("click", () => {{
        modal.classList.add("open");
      }});
      document.getElementById("btn-cancel-reset").addEventListener("click", () => {{
        modal.classList.remove("open");
      }});
      document.getElementById("btn-confirm-reset").addEventListener("click", () => {{
        completedSessions.clear();
        saveProgress();
        renderSchedule();
        updateMetrics();
        updateCharts();
        modal.classList.remove("open");
      }});

      // Instalação PWA no Android / Desktop
      const btnInstall = document.getElementById("btn-install-pwa");
      if (btnInstall) {{
        btnInstall.addEventListener("click", async () => {{
          if (!deferredPrompt) {{
            alert("Para instalar no Android:\\n1. Abra este link no Google Chrome.\\n2. Toque nos 3 pontinhos (⋮) no topo direito.\\n3. Selecione 'Instalar aplicativo' ou 'Adicionar à tela inicial'.");
            return;
          }}
          deferredPrompt.prompt();
          const choice = await deferredPrompt.userChoice;
          console.log('[PWA] Escolha do usuário:', choice.outcome);
          deferredPrompt = null;
          btnInstall.style.display = "none";
        }});
      }}
    }}

    // Iniciar tudo ao carregar o DOM
    document.addEventListener("DOMContentLoaded", initApp);
  </script>
</body>
</html>
"""
    HTML_FILE.write_text(html_content, encoding="utf-8")
    INDEX_FILE.write_text(html_content, encoding="utf-8")
    print(f"HTML gerado com sucesso: {HTML_FILE} ({len(html_content)} caracteres)")
    print(f"Index HTML gerado com sucesso: {INDEX_FILE} ({len(html_content)} caracteres)")

def main():
    days = parse_cronograma_md()
    print(f"Total de dias extraídos: {len(days)}")
    for d in days[:3]:
        print(f"Dia {d['dayNumber']}: {d['date']} ({d['weekday']}) - {len(d['sessions'])} sessões")
    generate_html(days)

if __name__ == "__main__":
    main()
