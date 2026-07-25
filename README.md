# SDD Workshop Boost

**Skill-Driven Development — Distribución de skills de metodología**  
**Versión:** 1.0.0 | **Tipo:** Exclusivo de workshop

Instala 19 skills de metodología de nivel producción en tu entorno de Claude Code. Estas skills se extrajeron de 197.831 líneas de código de producción real construido en 11 días: codifican las lecciones aprendidas, no “mejores prácticas” teóricas.


## Qué se instala

**19 skills → `~/.claude/skills/common/`** (activas en cada sesión de Claude, en cada proyecto)

| Categoría | Skills | Pilares |
|-----------|--------|---------|
| Navegador de metodología | `sdd-context` | Todos |
| Ingeniería de contexto | `claude-md-guidelines`, `skill-routing-decisions`, `skill-navigator-pattern`, `context-engineering-audit` | 1, 6 |
| Verificación y calidad | `fear-driven-development`, `verification-patterns`, `tdd-workflow`, `regression-prevention`, `proactive-bug-hunting` | 3 |
| Orquestación de IA | `directed-synthesis` | 4 |
| Disciplina de proceso | `github-workflow` | 5 |
| Comunicación | `tone-of-voice`, `writing-patterns`, `documentation-style`, `docs-organization` | 1 |
| Patrones de ingeniería | `change-tracking`, `smart-file-matching`, `java-record-breaking-changes` | — |

**3 templates** (scaffolding de proyecto, opcionales):
- `CLAUDE.md` — archivo de contexto del proyecto (rellena los huecos)
- `LEARNINGS.md` — bitácora de aprendizaje continuo (Pilar 6)
- `skill-template.yaml` — template mínimo de 3 secciones para tu primera skill de dominio