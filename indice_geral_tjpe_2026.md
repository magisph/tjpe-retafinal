# Índice Geral e Estrutura do Acervo TJ-PE 2026

Guia de navegação rápida e indexação de todos os arquivos do acervo de preparação para a Magistratura TJ-PE (Banca FGV).

## Arquivos do Acervo

1. `cronograma_tjpe_fgv.json`: Arquivo mestre de dados estruturados com metadados, ranking de disciplinas, matriz semanal e a régua completa de 108 dias.
2. `cronograma_tjpe_fgv.md`: Documentação textual completa de 108 dias com divisão de carga diária, tópicos de estudo novo e planos de revisão.
3. `mapeamento.json`: Definição estruturada em TypeScript das 14 disciplinas e seus subtemas estatísticos.
4. `mapeamento_disciplinas_fgv.md`: Mapeamento estatístico verticalizado com todas as tabelas de incidência e curva de relevância temática.
5. `generate_cronograma_tjpe_fgv.py`: Script gerador do algoritmo de distribuição de matérias, cálculo de prazos e pareamento de ciclos.
6. `guia_metodologia_tjpe_fgv.md`: Metodologia de estudos em 4 ciclos, protocolos de engenharia reversa FGV e regras de revisão.

## Instruções de Consulta via Custom PageIndex RAG
- Utilize `search_documents` para localizar qualquer tema (ex: 'usucapião', 'litisconsórcio', 'prisão preventiva', 'dia 045', 'revisão').
- Utilize `browse_documents` para navegar na árvore de documentos disponíveis.
- Utilize `get_document_structure` para inspecionar os sumários e páginas de cada arquivo.
- Utilize `get_page_content` para ler páginas ou intervalos específicos.
