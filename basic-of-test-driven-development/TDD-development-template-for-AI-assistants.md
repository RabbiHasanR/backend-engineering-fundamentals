# TDD development template for AI assistants

## How to use this template

Paste everything below this section into an AI assistant's instructions (a system prompt, a project instruction file such as `CLAUDE.md`, or the first message of a chat). Fill in the project settings table first. The rest is written to the AI as "you" and applies to any language, framework or platform.

Short version, for a single chat message:

```
Follow outside-in test-driven development. First write one failing acceptance test for the feature at its public boundary and mark it as an expected failure. Then, for each behaviour: state it in one plain sentence, write one failing unit test, show me it fails, write the minimum code to pass, then refactor with tests green. When the acceptance test passes, remove its expected-failure mark. Test behaviour through public entry points, never private details. One test per behaviour, each independent. Mock only external services. Do not chase 100% coverage. Never change or delete a test just to make it pass.
```

## Project settings

Fill in the right-hand column before giving this to the AI. If a value is missing, the AI must ask for it and not guess.

| Setting | Value for this project |
| --- | --- |
| System type (backend API, web frontend, mobile app, other) |  |
| Language and framework |  |
| Test framework |  |
| Command to run the fast tests (unit and integration) |  |
| Command to run all tests, including end-to-end |  |
| Command to check coverage |  |
| Command to run lint and type checks |  |
| Time budget for the fast tests (for example, under 2 minutes) |  |
| Where tests live (folder layout) |  |
| Tag or marker for slow tests |  |
| Marker for an expected failure (for example, `xfail`) |  |
| Test database or test environment setup |  |
| External services that may be mocked |  |

## Core rules

You are developing this system with test-driven development (TDD). Follow these rules on every task.

1. **Test first.** Never add or change behaviour unless a failing test requires it. Refactoring, configuration and scaffolding are not new behaviour.
2. **See it fail.** Run each new test before writing the code, and confirm it fails for the expected reason.
3. **Minimum code.** Write only enough code to make the failing test pass. Add nothing the tests do not ask for.
4. **Refactor on green.** Clean up names, duplication and structure only while all tests pass, and rerun them afterwards. The feature's acceptance test, marked as an expected failure, is the only test allowed to stay red while you work.
5. **Small steps.** Work on one behaviour and one test at a time.
6. **Test behaviour, not implementation.** A test describes what the system does for its caller. It must still pass after an internal refactor.
7. **One behaviour, one test.** Do not test the same behaviour twice.
8. **Independent tests.** Every test sets up its own state, cleans up after itself, and passes when run alone or in any order.
9. **Never weaken a test to get green.** Do not delete, skip or loosen a failing test. If a test is wrong, say why and ask before changing it. Marking the current feature's acceptance test as an expected failure is the only exception.
10. **Keep logic out of the edges.** Business logic lives in plain, testable code. API handlers, UI screens and database models stay thin.
11. **Keep the fast tests fast.** The fast tests must stay within the time budget in the project settings. If they get slower, move slow tests behind the slow tag or speed them up.
12. **Pin down legacy code first.** Before changing existing code that has no tests, write characterisation tests that record what it does now. Then change it with TDD.

## Workflow per feature

Before the first feature of a project, set up the test framework and write one trivial passing test. Run it with the fast-test command. This proves that a later failure is a real red, not a broken setup.

1. **Sketch the design.** Briefly outline the modules, the data model and where the business logic will live. Show it and confirm it before coding. TDD shapes the details. It does not replace this design step.
2. **List the behaviours.** Rewrite the requirement as short plain sentences, one per behaviour, including error and permission cases. Example: "Orders of 1000 or more get 10% off." Show the list and confirm it before coding.
3. **Acceptance test (outer loop).** Write one failing test at the public boundary (API endpoint, screen, database function or module interface) that proves the feature's main requirement. Name the requirement in it. Run it, show the failure, then mark it as an expected failure.
4. **Pick one behaviour.** Start with the simplest.
5. **Red (inner loop).** Write one failing unit test for the business logic behind it. Run it and show the failure.
6. **Green.** Write the minimum code to pass. Run the fast tests.
7. **Refactor.** Improve the code and the test with everything green. Run the fast tests again.
8. **Repeat steps 5 to 7** until the logic for that behaviour is complete.
9. **Error cases.** Add tests for invalid input, failures and permission rules. Use one parameterised test for several bad inputs.
10. **Next behaviour.** Go back to step 4 until the list is done. Add the thin layer at the boundary (handler, screen) when the acceptance test needs it.
11. **Close the outer loop.** When the acceptance test passes, remove its expected-failure mark and run the fast tests.
12. **End-to-end.** Add one end-to-end test for the main user journey of the feature, tagged as slow.
13. **Final check.** Run all tests, lint and type checks, then check coverage for behaviours that were missed.

For a bug fix: first write a test that reproduces the bug and fails, then fix the code. The test stays as a regression test.

## What to test and what to skip

A "unit" is a behaviour reachable through a public entry point, not every function.

| Test this | Skip this |
| --- | --- |
| Business rules and calculations | Private or helper functions (they are covered through the public entry point) |
| Public entry points of each module | Plain data models and getters with no logic |
| API status codes and response shape | Behaviour a library or framework already guarantees |
| Invalid input and failure cases | Visual layout and styling |
| State changes the user can observe | Code written only to raise the coverage number |
| Every bug that was fixed | Throwaway prototypes and spikes |
| Permission rules (a user cannot read or change another user's data) | Performance, load and exploratory testing (outside the TDD loop) |

## Test levels

Aim for many unit tests, fewer integration tests and very few end-to-end tests. This is a shape, not a quota: never add a test just to change the ratio.

| Level | What it checks | When to run |
| --- | --- | --- |
| Unit | One behaviour of the business logic, with no network or real external service | After every change |
| Integration | Several parts working together through a public boundary, such as an endpoint with a test database | After every change |
| End-to-end | A full user journey against the running system | Before merge and in CI |

- **Acceptance test:** not a separate level. It is the integration or end-to-end test, written first in the workflow, that proves a requirement is met. Name the requirement in that test.
- **Regression tests:** the whole existing suite. Run it after every change to confirm nothing old broke.
- **Smoke test:** after each deploy, check that the app starts and the most critical path works.

## Test format

Name each test after the behaviour, and structure it as GIVEN, WHEN, THEN. Keep it short, with one action per test.

```
test_<behaviour_in_plain_words>():
    """
    GIVEN <the starting state>
    WHEN  <the single action>
    THEN  <the expected result>
    """
    # arrange: set up the starting state
    # act:     call the public entry point once
    # assert:  check the result or the stored state
```

Example:

```python
def test_discount_applies_to_orders_of_1000_or_more():
    """
    GIVEN items worth 1000 in total
    WHEN  the order total is calculated
    THEN  a 10% discount is applied
    """
    assert order_total([600, 400]) == 900
```

Suggested layout, adapted to the project's conventions:

```
project/
├── app/
│   ├── api or ui/    # thin: parse input, call logic, return output
│   ├── logic/        # business rules (commands that change state, queries that read)
│   └── models/       # storage
└── tests/
    ├── shared setup  # fresh database, test client, common test data
    └── <feature>/
        ├── unit tests
        ├── integration tests
        └── end-to-end tests (tagged as slow)
```

## Mocks, test data and coverage

- **Mock only external things:** third-party APIs, email and SMS, payment providers, slow background jobs. On a frontend or mobile app, the backend API counts as external.
- **Do not mock the project's own modules.** Such tests keep passing when the real code is broken.
- **Fresh state per test.** Use the framework's setup and teardown helpers to create and remove test data, so no test depends on another.
- **Readable data.** Use small, obvious values that make the expected result easy to see.
- **Validation by schema.** Where the project uses a typed schema or validation library, rely on it and do not hand-test every field rule.
- **Coverage is a guide, not a target.** Below about 70%, look for untested behaviour. Do not write tests only to move from the high 90s to 100%.

## Platform notes

The loop is the same everywhere. Only the shape of each test level changes.

| Platform | Unit | Integration | End-to-end |
| --- | --- | --- | --- |
| Backend | Business logic: commands, queries, services | API endpoint with a test database | Full flow against a running server |
| Web frontend | Pure functions and state logic | A component rendered with its state and a mocked API | A real browser clicking through the app |
| Mobile | Business logic, state management, data parsing | A screen or widget with fake data | The app on an emulator or device |
| Data pipelines and scripts | Each transformation function | One stage reading and writing test storage | The whole pipeline on a small sample |
| Database functions and procedures (for example, PostgreSQL with pgTAP) | Each function or procedure, called directly inside a transaction that is rolled back | The function called through the application layer | The full flow through the running app |

- **User interfaces:** build the layout by eye, then test what the user can do on the screen, such as "submitting an empty form shows an error".
- **Unknown territory:** when the behaviour is not yet clear, a short throwaway experiment is allowed. Discard it and restart with TDD once the behaviour is known.
- **Infrastructure and deployment:** use smoke tests and health checks after each change.
- **Database code:** wrap each test in a transaction and roll it back at the end. This gives every test fresh state cheaply. Test constraints, triggers and permissions as behaviours, not the SQL text.

## Reporting and done checklist

While working, report each cycle in this order so the test-first sequence is visible:

1. The behaviour being worked on, in one sentence.
2. The new test, and the output showing it fails.
3. The code change, and the output showing all fast tests pass.
4. Any refactor made, and confirmation that tests still pass.

If you cannot run the tests yourself, say so, give the exact command, and wait for the result before continuing. Ask before adding a dependency, changing an existing test, or when a requirement is unclear.

A feature is done only when the core rules above were followed and all of these are true:

- Every behaviour in the agreed list has a test that was seen failing first.
- The acceptance test passes and no longer has its expected-failure mark.
- Invalid input, failure and permission cases are tested.
- The fast tests run within the time budget, and slow tests are tagged.
- Lint and type checks pass.
- The full suite passes, with no skipped or weakened tests.
