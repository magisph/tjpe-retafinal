# TJ-PE 2026 · Cronograma Tático de Reta Final — Magistratura Estadual (FGV)

> **Aplicação Web & PWA**: [https://magisph.github.io/tjpe-retafinal/](https://magisph.github.io/tjpe-retafinal/)  
> **Concurso**: Tribunal de Justiça do Estado de Pernambuco (TJ-PE) — Edital 2026  
> **Cargo**: Juiz Substituto do Estado de Pernambuco  
> **Banca Examinadora**: Fundação Getulio Vargas (FGV Conhecimento)  
> **Data da Prova Objetiva**: 27 de Setembro de 2026  

---

## 📱 Acesso Direto & Instalação como App (PWA)

O aplicativo foi projetado como um **Progressive Web App (PWA)** com suporte completo a execução offline nativa em celulares, tablets Android e computadores.

### Link de Produção:
👉 **[https://magisph.github.io/tjpe-retafinal/](https://magisph.github.io/tjpe-retafinal/)**

### Como Instalar no Android (Celular e Tablet):
1. Acesse o link acima pelo **Google Chrome** no seu dispositivo Android.
2. Toque no botão dourado **📲 Instalar App** no topo da página.
   *(Ou toque no menu de 3 pontinhos `⋮` do Chrome e selecione **"Instalar aplicativo"** ou **"Adicionar à tela inicial"**)*.
3. O ícone oficial **TJPE 2026** será adicionado à sua tela inicial.
4. **Funcionamento 100% Offline**: O aplicativo funciona mesmo sem conexão com a internet ou em modo avião, graças ao Service Worker (`sw.js`) que armazena os ativos na memória local. O seu progresso de estudo é mantido com segurança no `localStorage` do dispositivo.

---

## 🎯 Visão Geral da Metodologia de Reta Final

O cronograma foi desenvolvido através de engenharia reversa sobre a base histórica de **1.800 questões da FGV** para a Magistratura Estadual e Ministério Público, cobrindo com exaustividade os **22 dias de preparação** até a véspera da prova.

- **Duração Total**: 22 dias contínuos (05/09/2026 a 26/09/2026).
- **Carga Horária Total**: **102.0 horas líquidas** (4h em dias úteis; 6h aos finais de semana e feriados).
- **Total de Sessões**: **66 sessões táticas** nominais com identificadores únicos.
- **Resolução de Questões**: 1 sessão obrigatória diária (Sessão 3) dedicada à engenharia reversa FGV (totalizando **460+ questões comentadas**).

### Estrutura em Três Fases:
- **Fase I (Dias 1 a 10) — Núcleo Duro Top FGV**:
  - Direito Constitucional, Administrativo, Civil, Processo Civil, Penal e Processo Penal.
- **Fase II (Dias 11 a 18) — Travamento do Bloco III & Humanística**:
  - Direito Tributário, Ambiental, Empresarial, Consumidor, Criança e Adolescente, Eleitoral e Formação Humanística (CNJ).
- **Fase III (Dias 19 a 22) — Blindagem de Véspera & Memorização Rápida**:
  - Legislação Estadual de Pernambuco (COJE, Regimento Interno do TJ-PE, Estatuto dos Servidores de PE), Súmulas Vinculantes, Teses Repetitivas e Tabela de Prazos Decadenciais/Prescricionais.

---

## 🛠️ Tecnologias Utilizadas

- **Frontend**: HTML5 Semântico, CSS3 Moderno com Design System (variáveis CSS, suporte a Dark/Light Mode, WCAG AAA).
- **Gráficos Analíticos**: [Chart.js 4.4.1](https://www.chartjs.org/) (Gráfico de Donut de progresso global e Gráfico de Barras Empilhadas de horas por fase).
- **PWA & Offline**: Web App Manifest (`manifest.json`), Service Worker (`sw.js`) com estratégia *Stale-While-Revalidate* e ícones adaptativos (*maskable icons*).
- **Persistência**: `localStorage` com suporte a importação e exportação de backups em formato `.json`.
- **Hospedagem**: GitHub Pages com HTTPS automático.

---

## 📂 Estrutura do Repositório

```text
├── index.html                           # Aplicação web e PWA principal
├── cronograma_interativo_tjpe_2026.html # Cópia idêntica de distribuição
├── manifest.json                        # Configurações e metadados PWA
├── sw.js                                # Service Worker e cache offline
├── .nojekyll                            # Desativa Jekyll no GitHub Pages
├── icons/                               # Ícones oficiais do PWA (192, 512, maskable)
│   ├── icon-192.png
│   ├── icon-512.png
│   ├── icon-maskable-192.png
│   ├── icon-maskable-512.png
│   ├── favicon.png
│   └── favicon-32.png
├── cronograma_reta_final_tjpe_2026.md   # Cronograma nominal exaustivo em Markdown
├── guia_metodologia_tjpe_fgv.md         # Manual metodológico de reta final
└── scripts geradores Python             # Automação e parse dos dados
```

---

## ⚖️ Licença e Uso

Material desenvolvido para uso educacional e preparação tática para o concurso da Magistratura do Estado de Pernambuco (TJ-PE 2026).
