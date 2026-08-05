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

## Exercise 4: Trust But Verify — The Template Pattern

The most expensive thing you can do with AI is use your smartest (and costliest) model for repetitive work. The template pattern fixes this.

**The pattern:**
1. Use Sonnet (smart, creative) to design the first complete implementation of something
2. Verify it manually — it becomes your template
3. Use Haiku (fast, cheap) for all subsequent implementations following that template

Cost difference: Sonnet vs Haiku tokens are roughly 20× cheaper. For repetitive work (50+ similar files), this matters.

### Step 1: Create the template

Pick something repetitive in your codebase. Good candidates:
- REST endpoints (if you have many)
- Domain validators (if you validate many fields)
- Repository methods (CRUD patterns)
- React components following a common pattern

Ask Sonnet to build the first one perfectly:

```
Build a complete REST endpoint for updating a customer's shipping address.
Include: controller, service, repository, DTOs, validation, error handling,
unit tests, and integration tests. Follow all patterns from our architecture
skill. This will become our template for future endpoints — make it exemplary.
```

Review it carefully. Fix anything wrong. This is your template.

### Step 2: Extract a template skill

Create a skill that describes the template pattern:

```yaml
name: rest-endpoint-template
description: Template for adding REST endpoints — Haiku-compatible pattern
version: 1.0.0
tags: [api, template, backend]

template:
  controller: |
    @RestController
    @RequestMapping("/api/v1/[resource]")
    @RequiredArgsConstructor
    public class [Resource]Controller {
        private final [Resource]Service service;

        @PutMapping("/{id}")
        public ResponseEntity<[Resource]Response> update(
                @PathVariable Long id,
                @Valid @RequestBody Update[Resource]Request request) {
            return ResponseEntity.ok(service.update(id, request));
        }
    }

  service: |
    @Service
    @RequiredArgsConstructor
    @Transactional
    public class [Resource]Service {
        private final [Resource]Repository repository;

        public [Resource]Response update(Long id, Update[Resource]Request request) {
            [Resource] entity = repository.findById(id)
                .orElseThrow(() -> new EntityNotFoundException("[Resource] not found: " + id));
            // apply updates
            [Resource] saved = repository.save(entity);
            return [Resource]Response.from(saved);
        }
    }

instructions: |
  # REST Endpoint Template Pattern

  ## For Haiku: follow the template exactly
  1. Copy the controller template, replace [Resource] with the actual entity name
  2. Copy the service template, replace [Resource] with the actual entity name
  3. Add validation annotations to request DTO (@NotNull, @Size, etc.)
  4. Write 3 tests: happy path, not found case, validation failure case
  5. Run mvn test — all tests must pass before considering done

  ## Do not invent new patterns
  Follow the template. If something doesn't fit, stop and ask.
```

### Step 3: Delegate repeating work to Haiku

Now for every new endpoint, use the cheaper model:

```
Using the rest-endpoint-template skill, add a PUT /api/v1/orders/{id}/status
endpoint that updates order status. Follow the template exactly.
Use claude-haiku-4-5 for this task.
```

The Haiku model follows the template you established. You verify the output, not the thinking.

---

## Exercise 5: Test Suite Expansion with Haiku

Your test suite is probably thinner than it should be. Every developer knows this. But writing tests is boring, so it doesn't happen.

Haiku can expand your test suite 10× faster than you can write tests manually — and it's cheap enough that the cost is negligible.

### Step 1: Find your coverage gaps

```
Run our test suite and identify the three classes or modules with the
lowest test coverage. For each one, list: what scenarios are currently
tested, and what scenarios are NOT tested (but should be).
```

### Step 2: Systematic expansion

Pick one class. Ask for comprehensive test coverage:

```
For CustomerService.validateCreditLimit(), write a comprehensive test suite.
Cover:
- Customer below credit limit (should pass)
- Customer exactly at credit limit (edge case)
- Customer above credit limit (should fail)
- Customer with no credit limit set (should pass — unlimited)
- Suspended customer (should fail regardless of limit)
- Null customer (should throw IllegalArgumentException)
- Zero-value order (should pass regardless of limit)

Use our test naming convention and AssertJ assertions. Run mvn test after
each test to confirm they pass.
```

### Step 3: Round-trip testing

For parsing or transformation code, round-trip tests are the most powerful:

```
For OrderSerializer, write round-trip tests that:
1. Create an Order object with all fields populated
2. Serialize it to JSON
3. Deserialize the JSON back to an Order
4. Assert the deserialized object equals the original

Test with: complete order, order with null optional fields, order with
empty line items, order with maximum line item count (100).
```

If serialization is correct, round-trips pass. If they fail, you found a real bug — guaranteed.

### The Haiku pattern for test expansion

For large-scale test generation (50+ test classes), use this prompt pattern:

```
I'm going to give you a list of methods that need tests. For each one,
write 3–5 test cases following our verification-patterns skill.
Write all tests, then I will run mvn test and report back any failures.

Methods to test:
- OrderRepository.findByCustomerAndStatus()
- LineItemValidator.validate()
- PriceCalculator.calculateWithDiscounts()
```

Let it generate everything. Run the tests. Fix failures. Move on.

---

## Exercise 6: Create Your QA Skill

By now you've done enough with AI that you know what it gets wrong in your codebase. It makes specific mistakes, misses specific things, forgets specific rules.

Encode all of that into a QA skill.

### Reflect on what went wrong today

Before writing the skill, ask yourself:
- What did the AI generate that you had to fix?
- What test did it write that was wrong?
- What convention did it ignore?
- What business rule did it not know about?

### Write the QA skill

File: `~/.claude/skills/[project-name]-qa-review.yaml`

```yaml
name: order-service-qa-review
description: Quality gate for all AI-generated code in the order service
version: 1.0.0
tags: [qa, review, quality-gate]

checklist:
  architecture:
    - No business logic in controllers (check: controller methods max 5 lines)
    - Constructor injection only (no @Autowired on fields)
    - Services annotated with @Transactional where DB writes happen
    - DTOs are records (immutable), domain objects are classes (mutable)

  business_rules:
    - Credit limit check happens at CONFIRMATION, not creation
    - Status transitions are validated (can't go backward)
    - Price captured at confirmation time, not order creation time
    - Suspended customers cannot create orders (not just credit-blocked)

  testing:
    - Every new method has at least 3 tests (happy path, error, edge case)
    - Integration tests use Testcontainers (not H2 in-memory)
    - Test names follow: methodName_condition_expectedBehaviour
    - All tests pass before considering a task done (run mvn verify)

  common_ai_mistakes_in_this_codebase:
    - Forgetting to handle Optional.empty() from repositories (causes NPE)
    - Using == instead of .equals() for String comparisons
    - Forgetting @Valid on @RequestBody parameters (validation silently skipped)
    - Adding logic to CustomerService instead of extracting to domain service

instructions: |
  # QA Review

  Before marking any task as complete, work through this checklist.
  For each item: verify, don't assume.

  If anything fails:
  1. Fix it
  2. Re-run mvn verify
  3. Only then mark done

  When you find a new class of mistake not in this list, add it.
```

### The update trigger

At the end of every session, run:

```
What mistakes did we fix today that aren't in our QA skill yet?
Suggest additions to the checklist.
```

The QA skill grows. The AI makes that class of mistake less often. Over weeks, it becomes remarkably reliable on your codebase.

---

## Continuous Learning: LEARNINGS.md

Create one more file at the root of your project:

```bash
touch LEARNINGS.md
```

Every time something surprising happens — a bug found, a pattern discovered, a constraint violated — add it:

```markdown
# LEARNINGS.md

## 2026-03-05
- **Discovery**: OrderRepository.findByCustomer() is O(n) — does not use the index
  on customer_id. Fixed by adding @Query with explicit JOIN FETCH.
  **Pattern**: Always check EXPLAIN ANALYZE on repository queries that return lists.

- **AI mistake**: Claude generated a converter that lost timezone info when
  converting OffsetDateTime to LocalDateTime. Always use OffsetDateTime end-to-end.
  **Added to QA checklist.**

- **Skill updated**: order-service-qa-review.yaml — added timezone check.
```

Reference it in your CLAUDE.md:

```markdown
## Learning Log
See LEARNINGS.md for codebase-specific discoveries and gotchas.
Always check it before working on a new feature.
```

Now every session starts with the accumulated knowledge of every session before it.

---

## Bonus: Knowledge Context Protocol (KCP)

Everything you built today — CLAUDE.md, skills, LEARNINGS.md — is knowledge context. KCP makes that context machine-navigable.

A `knowledge.yaml` manifest at the project root tells any AI agent what exists and where to find it. Instead of making 30+ exploratory tool calls to understand your project, an agent with a manifest makes 3.

Measured result: **33 tool calls → 3 tool calls** for a standard orientation question.

### Create your knowledge.yaml

```bash
claude "Create a knowledge.yaml manifest for this project following the
KCP specification. Include all skills, docs, the CLAUDE.md, and
LEARNINGS.md. Group by type."
```

Or start from the 5-minute guide: https://wiki.totto.org/blog/2026/02/28/add-knowledgeyaml-to-your-project-in-five-minutes/

The spec: https://cantara.github.io/knowledge-context-protocol/

KCP v0.14 (March 2026) added query vocabulary — agents can now request skills filtered by audience, token budget, or capability. Already used across 110+ repos with 289 pre-built manifests for common CLI tools.

---

## What You've Built

By the end of these exercises, you have:

| Asset | What it does |
|-------|-------------|
| `CLAUDE.md` | Persistent project context — every session starts informed |
| Architecture skill | AI knows your patterns and layer rules |
| Domain skill | AI knows your business rules and terminology |
| QA skill | AI knows what "done" looks like in your codebase |
| QA review skill | AI self-checks before marking tasks complete |
| `LEARNINGS.md` | Accumulating knowledge base — compounds daily |
| `knowledge.yaml` | Navigation manifest — 10× faster agent orientation |

This is the **knowledge layer**. The code you write is the output. The knowledge layer is what makes every future session faster, cheaper, and more accurate.

---

## The First 30 Days

**Week 1:** Add 2–3 new skills. Update your QA skill after every session.

**Week 2:** Use the template pattern on something repetitive. Measure time saved.

**Week 3:** Review your skills — which ones have you used most? Make them better.

**Week 4:** Share your top 3 skills with a colleague. Their AI now knows your team's patterns.

The compounding effect becomes visible around week 3–4. Sessions that used to require back-and-forth corrections start landing correctly on the first try. That's the skill library paying off.

---

## Appendix: Skill File Locations

Skills live in `~/.claude/skills/`. They're global — available in all projects.

```
~/.claude/skills/
├── [project]-architecture.yaml     # project-specific
├── [project]-domain.yaml           # project-specific
├── [project]-qa.yaml               # project-specific
├── [project]-qa-review.yaml        # project-specific
└── common/                          # shared across all projects
    ├── verification-patterns.yaml
    ├── github-workflow.yaml
    └── tdd-workflow.yaml
```

To use a skill: reference it by name in your prompt. You can also add a plain instruction to CLAUDE.md (e.g. "Always use the [project]-architecture skill when working on backend code") — Claude reads this at session start and applies it automatically.

## Appendix: Quick Reference Commands

```bash
# Start a session in your project
cd your-project && claude

# Run all tests (adjust for your build tool)
mvn verify          # Maven
gradle test         # Gradle
npm test            # Node

# Check what skills exist
ls ~/.claude/skills/

# Add to CLAUDE.md to always use specific skills (plain instruction, not YAML):
# "Always use the [project]-architecture and [project]-domain skills."
```

---



