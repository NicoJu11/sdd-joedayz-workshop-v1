# Skill-Driven Development: A Hands-On Tutorial



**Methodology:** Skill-Driven Development (SDD)
**Time to complete:** 6–8 hours (workshop pace) or self-paced
**Tech stack:** Language-agnostic (examples in Java/Spring Boot and TypeScript/React)

---

## Why SDD (and not just prompting)

Most developers use AI like a search engine: ask a question, get an answer, move on. Each session starts from scratch. The AI doesn't know your codebase, your team's conventions, or the mistakes you made last week.

Skill-Driven Development treats AI as a **system**, not a tool. You build a library of reusable skills — each one encoding domain knowledge, instructions, and verification criteria. Every session starts with that library loaded. Every mistake you fix improves the library. The AI gets better at your codebase every day you use it.

The compound effect is real. In 11 days, a single developer built a 197,831-line Java library using SDD — what takes 10–18 months the traditional way. The skills library grew to 75 entries. Each new skill made the next task faster. By day 11, the AI was operating at the level of a senior architect who had been on the project from the beginning.

More recently: at an Item Consulting workshop in March 2026, a participant shipped 15,500 lines of code, 326 tests, and 82% coverage in 2 days — starting from scratch on an unfamiliar codebase. Same methodology.

This tutorial teaches you to build that system on your own codebase.

---

## Prerequisites

Before starting, verify:

```bash
claude --version          # should print version number
claude doctor             # should show green checkmarks
```

You also need:
- **A codebase** with at least some working code (ideally a real project you care about)
- **Git** (`git status` should work in your project directory)
- **Your build tool** running: `mvn test` or `npm test` or `gradle test` — something should pass

**Don't have a codebase?** 


If `claude doctor` fails, see [the setup guide](https://docs.anthropic.com/en/docs/claude-code) before continuing.

---

## Exercise 1: Baseline Assessment

Before you improve anything, measure where you are. This creates your reference point — and often surfaces things you didn't know you didn't know.

### What to run

Open Claude Code in your project directory:

```bash
cd your-project
claude
```

Then ask:

```
Analyse this codebase and give me:
1. Overall architecture pattern (MVC, hexagonal, layered, etc.)
2. Test count and estimated coverage
3. Three biggest technical risks or debt areas
4. How long the build takes
5. Dependencies that are outdated or unusual

Be specific. Use actual class names, file paths, and numbers where possible.
```

### What good output looks like

```
Architecture: Layered (controller → service → repository). Spring Boot 3.2.
Standard MVC pattern — no hexagonal or clean architecture separation.

Tests: 47 unit tests, 12 integration tests. Maven Surefire reports ~61% line coverage.
No mutation testing configured.

Technical risks:
1. CustomerService.java (847 lines) — god class. Everything touches it.
   Methods: createCustomer, updateCustomer, deleteCustomer, sendWelcomeEmail,
   generateInvoice, processPayment... this needs breaking up.
2. No contract testing. OrderController and the downstream InventoryService share
   assumptions that aren't verified anywhere.
3. build.gradle still pins Spring Boot 2.7.18. EOL January 2024.

Build time: mvn test takes 3m 42s (slow — mostly integration tests hitting H2).

Unusual deps: commons-lang 2.6 (ancient, should be commons-lang3) and
guava 20.0 (current is 33.x).
```

### Record what you found

Write three sentences summarising: what the architecture is, what the biggest risk is, and what you'll focus on today.

---

## Exercise 2: Write Your CLAUDE.md

`CLAUDE.md` is the first thing Claude Code reads when you open it in a project. It's your persistent context: conventions, constraints, domain knowledge, and working agreements. Every session starts with it. You write it once and refine it over time.

### Create the file

At the root of your project:

```bash
touch CLAUDE.md
```

Then open Claude Code and ask:

```
Based on your analysis of this codebase, help me write a CLAUDE.md file.
Include: project overview, architecture, key conventions, test strategy,
important constraints, and anything an experienced developer joining the
team would need to know in the first hour.

Format: markdown headers, be specific, use actual class and package names.
```

### Review and edit the draft

Claude will generate a starting point. Your job is to:
1. Remove anything that's wrong
2. Add anything it missed (especially business rules it can't infer from code)
3. Make the constraints section strong — this is where you prevent the AI from doing stupid things

### What a good CLAUDE.md looks like

```markdown
# OrderService — Claude Development Guide

## Project Overview
REST API for order management. Java 21, Spring Boot 3.2, PostgreSQL.
Deployed to Azure Kubernetes. ~30K LOC, 59 tests.

## Architecture
Layered: Controller → Service → Repository
- `com.example.order.api` — REST controllers (request/response DTOs)
- `com.example.order.domain` — business logic (services, domain objects)
- `com.example.order.infrastructure` — JPA repositories, external API clients

## Key Conventions
- Naming: `*Controller`, `*Service`, `*Repository` — always suffix
- DTOs are immutable records: `public record CreateOrderRequest(String customerId, ...)`
- Never put business logic in controllers — it goes in services
- Repository methods return `Optional<T>` — never null

## Test Strategy
- Unit tests: JUnit 5 + AssertJ. No Spring context in unit tests.
- Integration tests: `@SpringBootTest` + Testcontainers (real PostgreSQL)
- Run: `mvn test` (unit), `mvn verify` (all including integration)
- Coverage threshold: 80% line coverage enforced in CI

## Constraints
- NEVER commit directly to main — always PR
- NEVER use field injection (@Autowired on fields) — constructor injection only
- NEVER catch and swallow exceptions — log or rethrow with context
- All database migrations via Flyway — no schema changes outside migrations
- CustomerService is a known god class — don't add more to it

## What's In Progress
- Breaking up CustomerService (PaymentService extracted Feb 2026)
- Upgrading Spring Boot from 2.7 to 3.2 (in progress, blocking tests on auth module)
```

### The most important section: Constraints

The constraints section teaches Claude what NOT to do. List things that have gone wrong before. List your team's non-negotiables. The AI will follow them.

---

## Exercise 3: Your First Three Skills

A skill is a directory containing a `SKILL.md` file that tells the AI how to do a specific task in your codebase. Skills live in `~/.claude/skills/`. They're loaded on demand.

```
~/.claude/skills/
├── my-project-architecture/
│   └── SKILL.md
├── order-domain/
│   └── SKILL.md
└── my-project-qa/
    └── SKILL.md
```

You need three types to start:

1. **Architecture skill** — how your system is structured (patterns, naming, layers)
2. **Domain skill** — what your business domain actually does
3. **QA skill** — how you verify that code is correct

### Skill structure

Every `SKILL.md` has the same shape:

```markdown
# [Skill Name]

> description: One sentence: what this skill enables

## Context
What the AI needs to know before starting

## Steps
1. Step one
2. Step two
3. Step three

## Verification
- How to confirm it worked
- What tests to run
- What to check manually
```

### Skill 1: Your architecture skill

```bash
mkdir -p ~/.claude/skills/[project-name]-architecture
```

File: `~/.claude/skills/[project-name]-architecture/SKILL.md`

Ask Claude to draft it:

```
Create a skill file at ~/.claude/skills/[project-name]-architecture/SKILL.md
It should help any AI agent working on this codebase understand:
- Layer structure and what goes where
- Naming conventions
- How dependencies flow (what can call what)
- Common patterns used (factories, builders, events, etc.)
- Anti-patterns we explicitly avoid

Write the file directly to that path.
```

Edit the output. Add anything it missed. Especially: gotchas that bit you before.

### Skill 2: Your domain skill

```bash
mkdir -p ~/.claude/skills/[domain-name]-domain
```

File: `~/.claude/skills/[domain-name]-domain/SKILL.md`

```
Create a skill file at ~/.claude/skills/[domain-name]-domain/SKILL.md
Capture our domain model. Include:
- The main domain concepts and what they mean (use our actual terminology)
- Key business rules (what's valid, what's not)
- Important invariants — things that must always be true
- Domain events or state machines if relevant
- Examples of correct domain usage

This is our business language, not our code structure.
Write the file directly to that path.
```

Example of a strong domain skill:

```markdown
# Order Domain

> description: Domain model and business rules for the order management system

## Core Concepts
- **Order**: A request to purchase one or more products. Has a lifecycle:
  DRAFT → CONFIRMED → PICKING → SHIPPED → DELIVERED (or CANCELLED at any stage)
- **LineItem**: A specific product + quantity within an order
- **Customer**: Has a credit limit. Orders can be blocked if credit exceeded.
- **Fulfilment**: The physical process of picking, packing, shipping

## Key Business Rules
- An order CANNOT be confirmed if any LineItem has zero quantity
- Customer credit check happens at CONFIRMATION, not at DRAFT creation
- SHIPPED orders cannot be cancelled — must go through returns process
- Prices are fixed at confirmation time, not order creation
- A customer can have max 5 CONFIRMED orders pending at once

## Invariants
- Order total = sum of (lineItem.price × lineItem.quantity)
- Order status only moves forward (no going back from CONFIRMED to DRAFT)
- Every order MUST have a customer — orphan orders are a data integrity error

## Common Mistakes
- Confusing "order value" (at current prices) with "confirmed value" (at confirmation prices)
- Assuming cancellation is always possible — check status first
- Forgetting that credit check blocks confirmation, not creation
```

### Skill 3: Your first QA skill

```bash
mkdir -p ~/.claude/skills/[project-name]-qa
```

File: `~/.claude/skills/[project-name]-qa/SKILL.md`

```
Create a skill file at ~/.claude/skills/[project-name]-qa/SKILL.md
It should guide any agent doing test work to:
- Know what test types we use and when
- Know our test naming convention
- Know where test files live
- Know how to run tests and interpret output
- Know what counts as "done" from a quality perspective

Include our actual Maven/Gradle/npm commands.
Write the file directly to that path.
```

### Use your new skills

Test them immediately:

```
Using the order-domain skill, add a new domain rule: customers with
SUSPENDED status cannot create new orders. Add the validation to
OrderService and write tests for it.
```

Watch how the AI applies your domain rules and naming conventions automatically. That's the skill working.

---


