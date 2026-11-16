Here is a short study note on TDD from the article, starting with the core cycle as a diagram.

![alt text](image.png)

## What TDD is

TDD means you write the test before the code, in very small steps. The article's formula is **TDD = test-first development + refactoring**. Its main point is that the test works as a specification: writing it forces you to decide what the code should do before you write it.

## The steps

1. **Write one small test** for behaviour that doesn't exist yet.
2. **Run it and watch it fail.** This proves the test really checks something.
3. **Write just enough code** to make it pass, nothing extra.
4. **Run all the tests.** If anything fails, fix the code and rerun.
5. **Refactor.** Remove duplication and tidy the design while the tests stay green.
6. **Repeat** with the next test.

## Example (pytest)

Feature: an order total with a 10% discount at 1000 or more.

**Red: the test comes first, and fails because `order_total` doesn't exist.**
```python
# test_orders.py
from orders import order_total

def test_total_sums_item_prices():
    assert order_total([200, 300]) == 500
```

**Green: the smallest code that passes.**
```python
# orders.py
def order_total(prices):
    return sum(prices)
```

**Red again: the next behaviour.**
```python
def test_discount_applies_at_1000_or_more():
    assert order_total([600, 400]) == 900
```

**Green, then refactor: pass the test, then name the magic numbers.**
```python
DISCOUNT_THRESHOLD = 1000
DISCOUNT_RATE = 0.10

def order_total(prices):
    total = sum(prices)
    if total >= DISCOUNT_THRESHOLD:
        total -= total * DISCOUNT_RATE
    return total
```

## Two levels

| Level | Test describes | Typical tools |
|---|---|---|
| Acceptance TDD (also called BDD) | A requirement, from the user's view | Fitnesse, RSpec |
| Developer TDD | The design of one small piece of code | xUnit family (JUnit, PyUnit; pytest in Python) |

The ideal flow is one acceptance test first, then several developer-TDD cycles until it passes.

## What good tests look like

- They run fast.
- They run in isolation, so the order doesn't matter.
- They use data that is easy to read.
- Each one represents one small step toward the goal.

## Why it helps

- **Small steps make bugs easy to find.** A failure points at the few lines you just wrote.
- **Design improves.** Testable code tends to be loosely coupled and cohesive.
- **Tests become documentation.** They are working examples of how to call your code.
- **It scales.** The article cites a 4-year system with 250,000 lines of code and 4,000 tests running in under 20 minutes.

## Limits

- **It is not all your testing.** You still need integration, UI and exploratory testing.
- **100% coverage is not realistic.** Third-party code, UI and legacy parts are hard to cover.
- **It doesn't replace design thinking.** Sketch the architecture and requirements first, then use TDD for the build.
- **Slow suites need splitting.** Run a fast suite constantly and the full one in the background or on CI.
- **The whole team must agree to it.** It doesn't work if only some people do it.

## Applying it to your new project

1. Set up the test framework and a one-command test run before writing any feature code.
2. Sketch the overall design and data model lightly first.
3. For each feature, write one acceptance-level test (for example, an API endpoint test), then drive the internals with small unit tests.
4. Keep the fast suite under a few minutes and run the full suite in your CI pipeline on every push.
5. Agree on one rule with the team: no new function without a failing test first.










# TDD working note

## Core rules

1. **Test behaviour, not implementation.** Tests should describe requirements ("an article can be created"), so they survive refactoring and storage changes.
2. **One behaviour, one test.** Testing the same thing twice adds maintenance, and one bug then breaks many tests.
3. **Every test is independent.** Each test gets fresh state (for example, a new database) and runs in any order.
4. **Keep tests short, in three parts.** GIVEN the starting state, WHEN the action happens, THEN the expected result.
5. **Write the test first and watch it fail.** Only then write the code that makes it pass.
6. **Tests are code you must maintain.** Don't add tests only to raise a number.

## What to test, and what to skip

| Test this | Skip this |
|---|---|
| Public entry points of a module (the article's "commands" and "queries") | Private or helper methods, which are implementation details |
| Business rules (for example, a title must be unique) | Plain data models with no business logic |
| API responses: status code and response shape (schema) | Things a library already guarantees, such as its validation |
| Bad input returns a clean 400, not a 500 | Every line, just to reach 100% coverage |

A "unit" is a piece of behaviour reachable from outside the module, not every single function.

## Design that makes TDD easy

- **Separate business logic from the framework and the database.** The article uses commands (change state) and queries (read only). Route handlers stay thin and only call them.
- **Validate at the boundary with a typed schema library.** This removes many hand-written validation tests.
- **Use setup and teardown helpers** (fixtures in pytest) to create and clean test state automatically.

## Test levels

| Level | Checks | Rough share | When to run |
|---|---|---|---|
| Unit | One behaviour of the business logic | 50% | On every change |
| Integration | Units working together, for example an API endpoint | 30% | On every change |
| End-to-end | The whole app against a live server | 20% | Less often, or in CI |

Tag slow tests so you can exclude them during development. In a simple app, 40/40/20 is fine.

## Mocks and coverage

- **Mock only external things:** third-party APIs, email, slow async jobs.
- **Don't mock your own modules.** Such tests keep passing when the real code is broken, and they break on every refactor.
- **Coverage is a guide.** Under about 70%, add tests. Chasing 98% to 100% is usually wasted effort.

# Template for the team

## 1. Project layout

```
project/
├── app/
│   ├── api/          # thin handlers: parse request, call logic, return response
│   ├── commands/     # actions that change state
│   ├── queries/      # read-only actions
│   └── models/       # storage
└── tests/
    ├── shared setup  # fixtures: fresh DB, test client
    ├── config        # markers/tags such as "e2e"
    └── <feature>/
        ├── test_commands
        ├── test_queries
        ├── test_api
        └── schemas/  # expected response shapes
```

## 2. Workflow per feature

1. Write the requirements as short behaviour statements.
2. For each one, write a failing test for the command or query.
3. Write the minimum code to pass, then refactor.
4. Write a failing API test (status code and response schema), then add the thin handler.
5. Add bad-input tests using one parameterised test with several inputs.
6. Add one end-to-end test for the main user flow, tagged as slow.
7. Check coverage for gaps in behaviour, not for the number.

## 3. Test template

```
test_<behaviour>():
    """
    GIVEN <starting state>
    WHEN  <action>
    THEN  <expected result>
    """
    # arrange: set up the state
    # act:     call the public entry point once
    # assert:  check the result or the stored state
```

## 4. Review checklist

- [ ] The test was written first and seen failing.
- [ ] The name and GIVEN/WHEN/THEN describe a behaviour.
- [ ] It calls a public entry point, not a private method.
- [ ] It doesn't depend on another test or on leftover data.
- [ ] No other test covers this behaviour.
- [ ] Mocks are used only for external services.
- [ ] Error cases return proper client errors.
- [ ] Slow tests are tagged and excluded from the fast run.







These six terms describe tests along different axes, which is why they overlap: unit, integration and end-to-end are about **how much of the system** a test covers, acceptance and behaviour are about **whose point of view** it takes, and regression is about **why you run it**.

I'll use one example throughout: an online shop where orders of 1000 or more get a 10% discount.

## By scope: how much is tested

**Unit test.** Checks one small piece of logic alone, with no database or network. It runs in milliseconds.
```python
def test_discount_applies_at_1000():
    assert order_total([600, 400]) == 900
```

**Integration test.** Checks that several pieces work together, such as your API handler, business logic and database.
```python
def test_create_order_endpoint(client):
    response = client.post("/orders/", json={"items": [600, 400]})
    assert response.status_code == 201
    assert response.json()["total"] == 900   # saved and returned correctly
```

**End-to-end (e2e) test.** Checks a full user journey against the real running system, from the outside.
> A script opens the site, logs in, adds two products to the cart, checks out, and confirms the order page shows a total of 900 and a confirmation email is sent.

These are the slowest and most fragile tests, so you keep only a few.

## By viewpoint: who defines "correct"

**Acceptance test.** Checks that a feature meets the business requirement, as the customer or product owner would judge it. The question is "did we build the right thing?", not "is the code correct?".
> Requirement: "Customers who spend 1000 or more get 10% off." The acceptance test places such an order and checks the customer is charged 900. If it passes, the feature is accepted.

**Behaviour test (BDD).** The same idea as an acceptance test, but written in plain language that non-developers can read, usually as Given/When/Then. Tools then run that text as a test.
```gherkin
Scenario: Discount on large orders
  Given a cart with items worth 1000
  When the customer checks out
  Then the total charged is 900
```
The article you shared first treats acceptance TDD and BDD as the same thing.

## By purpose: why you run it

**Regression test.** Any test you re-run after a change to make sure old features still work. It is not a separate kind of test; your whole existing suite of unit, integration and e2e tests is your regression suite.
> You add a "free shipping" feature. The old discount test suddenly fails, because your change broke the discount. That test just caught a regression.

A common habit: whenever you fix a bug, first write a test that reproduces it, so it can never come back unnoticed.

## Other types worth knowing

| Type | What it checks | Example |
|---|---|---|
| Smoke test | The app starts and the most critical paths work at all; run right after a deploy | After deploying, hit `/health`, log in, and load the home page |
| System test | The complete, assembled system against its requirements, usually done by QA | QA tests the whole shop in a staging environment |
| User acceptance test (UAT) | Real users or the client try it before release | The shop owner places test orders and signs off |
| Contract test | Two services agree on the request and response format | The order service still sends the fields the payment service expects |
| Performance / load test | Speed and stability under heavy traffic | 5,000 users check out at once; response time stays under 500 ms |
| Stress test | Where and how the system breaks beyond its limits | Keep raising traffic until it fails, and check that it recovers |
| Security test | Protection against attacks and unauthorised access | A user cannot view another user's order by changing the ID in the URL |
| Exploratory test | A human freely pokes around to find surprises that scripts miss | A tester tries a negative quantity in the cart |
| Static checks | Problems found without running the code | Linters and type checkers |

## How they fit together

For the discount feature, you might have: several unit tests for the calculation, a couple of integration tests for the order endpoint, one e2e test for the checkout journey that also serves as the acceptance test, a smoke test after each deploy, and all of them together acting as your regression suite on every later change.