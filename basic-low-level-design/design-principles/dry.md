1. What Is the DRY Principle?
“Every piece of knowledge must have a single, unambiguous, authoritative representation within a system.” — The Pragmatic Programmer

The DRY principle says that each piece of knowledge in your system should live in exactly one place. When you need that knowledge somewhere else, you reference the single source rather than creating a second copy.

Notice the quote says "knowledge," not "code." This is an important distinction. DRY is not just about avoiding duplicate lines of code. It applies to:

Business rules: If "users must be 18 or older" is a rule, it should be defined once, not checked in five different places with slightly different age thresholds.
Configuration: Database connection strings, API keys, and timeout values should live in one config file, not scattered across multiple classes.
Data models: If a User has a name and email, that structure should be defined once, not redefined in every module that touches user data.
Documentation: If your API docs describe a field as "ISO 8601 date format," that definition should come from one source, not be manually written in three different doc pages.
Tests: Shared setup logic (like creating test users or populating a database) should be extracted into helpers rather than copy-pasted across test files.
Whenever the same concept appears in more than one place, you introduce redundancy. Redundancy makes your system harder to maintain and more prone to bugs.


The Rule of Three
Before you rush off to extract every bit of repeated code into a shared utility, there is an important guideline to keep in mind: the Rule of Three.

The idea is simple. Before extracting shared logic, wait until you see the same pattern three times. Two occurrences might be coincidental. Maybe those two pieces of code look similar today but will diverge tomorrow as their respective features evolve. Three occurrences, though, that is a pattern.

At that point, you have strong evidence that the duplication represents genuine shared knowledge, and extracting it into a single location is the right call.



Why Repetition Is a Problem
Duplication might seem harmless for small projects, but the problems compound as the codebase grows. Here are the four main reasons repeated knowledge is dangerous.

1. Harder to Maintain
When a rule or piece of logic changes, you must find and update every occurrence. In a small project, you might remember all three locations. In a codebase with 500 files and multiple contributors, you will not. Missing even one copy leads to inconsistent behavior that is difficult to trace.

2. Higher Risk of Bugs
More copies mean more chances for errors. Suppose the original validation checks email.contains("@"), but when someone copies it to a new module, they accidentally write email.contains("@") but forget the null check. Now one module crashes on null input while the others handle it gracefully. The bug is invisible until a null email reaches that specific module in production.

3. Bloated Codebase
Redundant logic adds noise. When reading through a codebase, you want to quickly identify what is unique versus what is shared. If the same 10-line validation block appears in 15 files, those 150 lines contribute nothing new. They just make the codebase harder to navigate and understand.

4. Poor Test Coverage
When logic is repeated, each copy needs its own tests. If you have email validation in three modules, you need three sets of tests to cover the same behavior. When someone adds a new validation rule, they need to remember to update all three test files as well. In practice, they usually update one, maybe two, and leave the third untested.



5. When it is Okay to Repeat
The DRY principle is a guideline, not a strict rule. There are situations where a bit of repetition produces better code than a forced abstraction.

1. Avoid Premature Abstractions
Do not extract shared code too early. Let duplication reveal itself first. Abstractions created too soon can be misleading or hard to maintain.

“Duplication is far cheaper than the wrong abstraction.” — Sandi Metz

2. Keep Tests Readable
Tests need to be easy to read in isolation. If a test fails, the developer reading it should be able to understand the setup, the action, and the expected result without jumping to five different helper methods.

Consider this test:

```python
def test_should_reject_invalid_email():
    user = User("Alice", "invalid-email")

    result = EmailValidator.is_valid(user.email)

    assert result is False

def test_should_accept_valid_email():
    user = User("Bob", "bob@example.com")

    result = EmailValidator.is_valid(user.email)

    assert result is True
```


Yes, new User(...) appears in both tests. You could extract it into a factory method. But doing so would force the reader to look elsewhere to understand what kind of user is being created. In tests, clarity beats brevity. A small amount of repetition is a reasonable trade-off for tests that tell their story from top to bottom.

3. Keep It Simple
If a line of code is extremely simple and unlikely to change, extracting it into a shared utility can actually make things worse. Creating a MathUtils.addOne(x) method to avoid writing x + 1 in two places is not DRY. It is overengineering. The overhead of finding, understanding, and navigating to the shared method outweighs the benefit of eliminating the trivial duplication.