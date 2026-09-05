from __future__ import annotations

import json
import re
from datetime import date, timedelta
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILL_ROOT = Path(r"C:\Users\Junior do Titico\.codex\skills\cronograma-magistratura-fgv")
MEDIA_PATH = SKILL_ROOT / "references" / "Media_Questoes.md"
MAP_PATH = SKILL_ROOT / "references" / "Mapeamento_Magis_Estadual_FGV.md"
OUT_DIR = ROOT / "outputs"
JSON_PATH = OUT_DIR / "cronograma_tjpe_fgv.json"
MD_PATH = OUT_DIR / "cronograma_tjpe_fgv.md"

START_DATE = date(2026, 6, 11)
END_DATE = date(2026, 9, 26)

WEEKDAY_PT = {
    "monday": "segunda-feira",
    "tuesday": "terça-feira",
    "wednesday": "quarta-feira",
    "thursday": "quinta-feira",
    "friday": "sexta-feira",
    "saturday": "sábado",
    "sunday": "domingo",
}

WEEKDAY_PT_TITLE = {
    "monday": "Segunda-feira",
    "tuesday": "Terça-feira",
    "wednesday": "Quarta-feira",
    "thursday": "Quinta-feira",
    "friday": "Sexta-feira",
    "saturday": "Sábado",
    "sunday": "Domingo",
}

WEEKLY_PAIRINGS = {
    "monday": ["Direito Processual Civil", "Direito Eleitoral"],
    "tuesday": ["Direito Civil", "Direito Ambiental"],
    "wednesday": ["Direito Penal", "Direitos Humanos"],
    "thursday": ["Direito Processual Penal", "Noções Gerais de Direito e Formação Humanística"],
    "friday": ["Direito Constitucional", "Direito Tributário e Financeiro"],
    "saturday": ["Direito Administrativo", "Direito Empresarial"],
    "sunday": ["Direito do Consumidor", "Direito da Criança e do Adolescente"],
}

CYCLE_INFO = {
    1: {
        "title": "Ciclo 1: Semanas 1 a 4 (Sólida Inicialização)",
        "activity": [
            "leitura ativa da fonte normativa",
            "fixação por quadro curto",
            "questões FGV com identificação de padrão de cobrança",
        ],
    },
    2: {
        "title": "Ciclo 2: Semanas 5 a 8 (Avanço e Densidade)",
        "activity": [
            "leitura dirigida com comparação entre institutos",
            "marcação de exceções e prazos",
            "questões FGV com engenharia reversa das alternativas",
        ],
    },
    3: {
        "title": "Ciclo 3: Semanas 9 a 12 (Legislação Local e Humanística)",
        "activity": [
            "releitura orientada por incidência",
            "mapa de pegadinhas normativas",
            "questões FGV com registro de erro recorrente",
        ],
    },
    4: {
        "title": "Ciclo 4: Semanas 13 a 17 (Simulados e Blindagem de Erros)",
        "activity": [
            "simulado setorial cronometrado",
            "correção ativa do caderno de erros",
            "revisão final por assertivas FGV",
        ],
    },
}


def parse_media() -> dict[str, dict[str, float]]:
    text = MEDIA_PATH.read_text(encoding="utf-8")
    rows: dict[str, dict[str, float]] = {}
    pattern = re.compile(r"\|\s*\*\*(?P<name>[^*]+)\*\*\s*\|\s*(?P<total>\d+)\s*\|\s*\*\*(?P<avg>[\d,]+)\*\*")
    for match in pattern.finditer(text):
        name = match.group("name").strip()
        if name.startswith("TOTAL"):
            continue
        rows[name] = {
            "totalQuestions": int(match.group("total")),
            "averagePerExam": float(match.group("avg").replace(",", ".")),
        }
    return rows


def parse_mapping() -> list[dict]:
    text = MAP_PATH.read_text(encoding="utf-8")
    disciplines: list[dict] = []
    discipline_pattern = re.compile(
        r'\{\s*id:\s*"(?P<id>[^"]+)",\s*name:\s*"(?P<name>[^"]+)",\s*totalQuestions:\s*(?P<total>\d+),\s*subtopics:\s*\[(?P<subs>.*?)\]\s*\}',
        re.S,
    )
    subtopic_pattern = re.compile(
        r'\{\s*id:\s*"(?P<id>[^"]+)",\s*name:\s*"(?P<name>[^"]+)",\s*questions:\s*(?P<questions>\d+),\s*percentage:\s*(?P<percentage>[\d.]+)\s*\}'
    )
    for discipline_match in discipline_pattern.finditer(text):
        subtopics = [
            {
                "id": sub_match.group("id"),
                "name": sub_match.group("name"),
                "questions": int(sub_match.group("questions")),
                "percentage": float(sub_match.group("percentage")),
            }
            for sub_match in subtopic_pattern.finditer(discipline_match.group("subs"))
        ]
        disciplines.append(
            {
                "id": discipline_match.group("id"),
                "name": discipline_match.group("name"),
                "totalQuestions": int(discipline_match.group("total")),
                "subtopics": subtopics,
            }
        )
    return disciplines


def media_for(name: str, media: dict[str, dict[str, float]]) -> dict[str, float]:
    if name in media:
        return media[name]
    if name.startswith("Noções Gerais"):
        return media["Noções Gerais e Formação Humanística"]
    raise KeyError(name)


def cycle_for(day_number: int) -> int:
    if day_number <= 28:
        return 1
    if day_number <= 56:
        return 2
    if day_number <= 84:
        return 3
    return 4


def select_subtopic(discipline: dict, occurrence: int, cycle: int) -> dict:
    subtopics = discipline["subtopics"]
    if not subtopics:
        raise ValueError(f"Disciplina sem subtemas: {discipline['name']}")
    if cycle == 1:
        index = occurrence % len(subtopics)
    elif cycle == 2:
        index = (occurrence + 3) % len(subtopics)
    elif cycle == 3:
        index = (occurrence + 7) % len(subtopics)
    else:
        index = (occurrence + 11) % len(subtopics)
    return subtopics[index]


def make_revision_plan(day_number: int, total_minutes: int, history: list[dict]) -> dict | None:
    if day_number < 8:
        return None
    candidates = []
    for offset in (7, 3, 14, 1):
        if len(history) >= offset:
            candidates.extend(history[-offset]["subjects"])
    seen: set[tuple[str, str]] = set()
    items = []
    for subject in candidates:
        key = (subject["name"], subject["subtopics"][0])
        if key in seen:
            continue
        seen.add(key)
        items.append(
            {
                "discipline": subject["name"],
                "subtopics": subject["subtopics"],
                "method": "questões FGV + releitura do erro ou destaque do estudo anterior",
            }
        )
        if len(items) == 2:
            break
    if not items:
        raise ValueError(f"Sem histórico para revisão no dia {day_number}")
    return {
        "minutes": int(round(total_minutes * 0.30)),
        "items": items,
    }


def build_schedule() -> dict:
    media = parse_media()
    disciplines = parse_mapping()
    by_name = {discipline["name"]: discipline for discipline in disciplines}
    ranking = []
    for rank, discipline in enumerate(sorted(disciplines, key=lambda item: item["totalQuestions"], reverse=True), start=1):
        media_row = media_for(discipline["name"], media)
        ranking.append(
            {
                "name": discipline["name"],
                "totalQuestions": discipline["totalQuestions"],
                "averagePerExam": media_row["averagePerExam"],
                "rank": rank,
            }
        )

    days = []
    occurrence_by_discipline = {discipline["name"]: 0 for discipline in disciplines}
    current = START_DATE
    day_number = 1
    while current <= END_DATE:
        weekday = current.strftime("%A").lower()
        cycle = cycle_for(day_number)
        total_minutes = 240 if weekday in {"saturday", "sunday"} else 180
        revision_minutes = 0 if day_number < 8 else int(round(total_minutes * 0.30))
        new_study_minutes = total_minutes - revision_minutes
        if day_number < 8:
            split = [new_study_minutes // 2, new_study_minutes - (new_study_minutes // 2)]
        elif total_minutes == 180:
            split = [70, 56]
        else:
            split = [92, 76]

        subjects = []
        for index, discipline_name in enumerate(WEEKLY_PAIRINGS[weekday]):
            discipline = by_name[discipline_name]
            occurrence = occurrence_by_discipline[discipline_name]
            subtopic = select_subtopic(discipline, occurrence, cycle)
            occurrence_by_discipline[discipline_name] += 1
            subjects.append(
                {
                    "name": discipline_name,
                    "minutes": split[index],
                    "subtopics": [subtopic["name"]],
                    "sourceSubtopicIds": [subtopic["id"]],
                    "activities": CYCLE_INFO[cycle]["activity"],
                }
            )

        entry = {
            "dayNumber": day_number,
            "date": current.isoformat(),
            "weekday": weekday,
            "weekdayPt": WEEKDAY_PT[weekday],
            "cycle": cycle,
            "totalMinutes": total_minutes,
            "newStudyMinutes": new_study_minutes,
            "revisionMinutes": revision_minutes,
            "subjects": subjects,
            "revisionPlan": make_revision_plan(day_number, total_minutes, days),
        }
        days.append(entry)
        day_number += 1
        current += timedelta(days=1)

    return {
        "metadata": {
            "exam": "TJ-PE - Magistratura Estadual - Prova Objetiva - Banca FGV",
            "startDate": START_DATE.isoformat(),
            "endDate": END_DATE.isoformat(),
            "totalDays": len(days),
            "weekdayMinutes": 180,
            "weekendMinutes": 240,
            "revisionStartsOnDay": 8,
            "canonicalSources": [
                "references/Media_Questoes.md",
                "references/Mapeamento_Magis_Estadual_FGV.md",
            ],
            "generationRules": {
                "subjectsPerDay": 2,
                "fixedWeeklyPairings": True,
                "cycles": 4,
                "revisionFromSecondWeek": "30% do tempo diário",
                "noInventedSubtopics": True,
            },
        },
        "disciplineRanking": ranking,
        "weeklyPairings": WEEKLY_PAIRINGS,
        "cycleStrategy": [
            {"cycle": cycle, "title": info["title"], "activities": info["activity"]}
            for cycle, info in CYCLE_INFO.items()
        ],
        "days": days,
    }


def render_subject(subject: dict) -> str:
    activities = "; ".join(subject["activities"])
    topics = "; ".join(subject["subtopics"])
    return f"**{subject['name']}** ({subject['minutes']} min): {topics}. Atividades: {activities}."


def render_revision(plan: dict | None) -> str:
    if not plan:
        return "Sem revisão obrigatória nesta primeira semana."
    items = []
    for item in plan["items"]:
        topics = "; ".join(item["subtopics"])
        items.append(f"{item['discipline']} - {topics}")
    return f"{plan['minutes']} min: " + " | ".join(items) + "."


def render_markdown(schedule: dict) -> str:
    lines: list[str] = []
    lines.append("# Cronograma Completo de Estudos - TJ-PE Magistratura FGV")
    lines.append("")
    lines.append("## 1. Diretrizes Estratégicas e Grade Fixa")
    lines.append("")
    lines.append(
        "Período canônico: 11/06/2026 a 26/09/2026, com 108 dias corridos. "
        "Carga: 180 minutos de segunda a sexta e 240 minutos aos sábados e domingos. "
        "A partir do dia 8, 30% do tempo diário é reservado à revisão de conteúdo já estudado."
    )
    lines.append("")
    lines.append("Ranking estatístico por questões históricas:")
    for row in schedule["disciplineRanking"]:
        lines.append(
            f"{row['rank']}. {row['name']} - {row['totalQuestions']} questões; média {row['averagePerExam']:.2f} por prova."
        )
    lines.append("")
    lines.append("## 2. Matriz Semanal Fixa de Disciplinas")
    lines.append("")
    lines.append("| Dia da Semana | Disciplina 1 (Tempo Devotado) | Disciplina 2 (Tempo Devotado) | Foco de Engenharia Reversa (Questões) |")
    lines.append("| :--- | :--- | :--- | :--- |")
    for weekday in ("monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"):
        pair = schedule["weeklyPairings"][weekday]
        base = "90 min na primeira semana; depois 70 min" if weekday not in {"saturday", "sunday"} else "120 min na primeira semana; depois 92 min"
        second = "90 min na primeira semana; depois 56 min" if weekday not in {"saturday", "sunday"} else "120 min na primeira semana; depois 76 min"
        lines.append(
            f"| {WEEKDAY_PT_TITLE[weekday]} | {pair[0]} ({base}) | {pair[1]} ({second}) | Alternativas FGV, exceções legais, jurisprudência cobrada e caderno de erros |"
        )
    lines.append("")
    lines.append("## 3. Cronograma Progressivo por Ciclos (Régua de 108 Dias)")
    current_cycle = None
    for day in schedule["days"]:
        if day["cycle"] != current_cycle:
            current_cycle = day["cycle"]
            lines.append("")
            lines.append(f"### {CYCLE_INFO[current_cycle]['title']}")
            lines.append("")
        lines.append(
            f"#### D{day['dayNumber']:03d} | {day['date']} ({day['weekdayPt']})"
        )
        lines.append(
            f"- Carga total: {day['totalMinutes']} min; estudo novo: {day['newStudyMinutes']} min; revisão: {day['revisionMinutes']} min."
        )
        lines.append(f"- {render_subject(day['subjects'][0])}")
        lines.append(f"- {render_subject(day['subjects'][1])}")
        lines.append(f"- Revisão: {render_revision(day['revisionPlan'])}")
        lines.append("")
    lines.append("## 4. Protocolo Operacional Diário (Instruções de Execução)")
    lines.append("")
    lines.append(
        "Em cada bloco de estudo novo, execute leitura ativa, fixação curta e questões FGV. "
        "Na revisão, resolva questões ou releia destaques apenas dos subtemas já estudados, registrando erros por disciplina e por subtema."
    )
    lines.append("")
    lines.append("## 5. Artefatos e Validação")
    lines.append("")
    lines.append(f"- JSON estruturado: `{JSON_PATH.name}`")
    lines.append(f"- Markdown completo: `{MD_PATH.name}`")
    lines.append("- Validação prevista: `python scripts/validate_schedule.py outputs/cronograma_tjpe_fgv.json --markdown outputs/cronograma_tjpe_fgv.md`")
    lines.append("")
    return "\n".join(lines)


def main() -> None:
    OUT_DIR.mkdir(exist_ok=True)
    schedule = build_schedule()
    JSON_PATH.write_text(json.dumps(schedule, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    MD_PATH.write_text(render_markdown(schedule), encoding="utf-8")
    print(JSON_PATH)
    print(MD_PATH)


if __name__ == "__main__":
    main()
