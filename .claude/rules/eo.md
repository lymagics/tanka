# Elegant Objects Coding Rules

---
## 1. General
### 1.1 Language
- Always use python type hints.
---
## 2. Naming
### 2.1 Class Names
- Never use class names ending in -er, -or, or -Utils (exceptions: User, Computer).
- Naming a class based on what its objects do is incorrect.
- Classes should be named based on what they are, not what they do.
- Think about what the objects will encapsulate and choose a name that represents that conceptual group.
### 2.2 Method Names
- A builder is a method that constructs or returns something.
- A builder never returns None, and its name must always be a noun (optionally with an adjective).

```python
def pow(self, base: int, power: int) -> int:
    pass


def speed(self) -> float:
    pass


def employee(self, id: int) -> Employee:
    pass


def parsed_cell(self, x: int, y: int) -> str:
    pass
```

- A manipulator is a method that modifies the real-world entity represented by an object.
- A manipulator always returns None (implicitly), and its name must always be a verb (optionally with an adverb).

```python
def save(self, content: str):
    pass


def put(self, key: str, value: float):
    pass


def remove(self, emp: Employee):
    pass


def quickly_print(self, id: int):
    pass
```

- If a builder returns a Boolean value, its name should be an adjective.
- The prefix is_ is redundant and should not be used, but temporarily adding it can help ensure the name sounds correct.

```python
def empty(self) -> bool:
    pass


def readable(self) -> bool:
    pass


def negative(self) -> bool:
    pass
```

- equals should be renamed to equal_to.
- exists should be renamed to present.
### 2.3 Variable Names
- Do not use compound names anywhere in the code.
- Every variable must have a name consisting of a single noun.
- Exceptions are allowed only when a single noun would lose its meaning without an adjective, for example: time_zone, side_effect, MicroService, ChangingRoom, washing_machine, bus_stop, laughing_ga.
---
## 3. Constructors
### 3.1 Constructor Design
- Prefer having one primary constructor.
- The more constructors a class has, the more flexibility it gives to clients using the class.
- Keep constructors code-free: they should only contain assignment statements.
- Allow only assignments in one primary constructor, delegating from secondaries.
- Use plum-dispatch python library for method overloading.

```python
from plum import dispatch


class Cash:
    @dispatch
    def __init__(self, value: float):
        self.__init__(int(value))

    @dispatch
    def __init__(self, value: str):
        self.__init__(int(value))

    @dispatch
    def __init__(self, value: int):
        self.dollars = value
```
---
## 4. Objects and Encapsulation
### 4.1 Attributes
- All encapsulated objects (attributes) are part of an object's identity.
- An object should encapsulate four or fewer attributes.
- If more attributes are required, they should be grouped into other objects.
- Together, these objects should form a structured tree of objects.
- An object that encapsulates nothing should not exist.
- Never create getters and setters.
- Never add an attribute or method to an object at runtime.
---
## 5. Interfaces and Methods
### 5.1 Interfaces
- Always use interfaces.
- Ensure that every public method in a class implements an interface.
- Keep interfaces minimal.
- Add convenience behavior through smart wrappers.

```python
# Instead of:
class Exchange(ABC):
    @abstractmethod
    def rate(
        self,
        target: str,
        source: str = "USD",
    ) -> float:
        pass


# Use:
class Exchange(ABC):
    @abstractmethod
    def rate(
        self,
        target: str,
        source: str,
    ) -> float:
        pass

    class Smart:
        def __init__(self, e: "Exchange"):
            self.origin = e

        def to_usd(
            self,
            source: str,
        ) -> float:
            return self.origin.rate(
                source,
                "USD",
            )


# Usage:
rate = Exchange.Smart(NYSE()).to_usd("EUR")
```
### 5.2 Methods
- The more methods a class exposes, the harder it becomes to use correctly.
- The number of public methods in a class should be five or fewer.
- Never create static methods.
- Long methods are forbidden.
- Methods with multiple return statements are forbidden.
---
## 6. Immutability
### 6.1 Immutable Objects
- All classes should be immutable.
- If modification is needed, create a new object instead.
---
## 7. Testing
### 7.1 Unit Tests
- Write unit tests instead of docstrings.
- Do not use mocks.
- Instead mocks, create fake classes that implement interfaces and use them in unit tests.
---
## 8. Constants
### 8.1 Avoiding Constants
- Do not use public constants.
- Instead, create a class that encapsulates the semantic meaning of the constant.

```python
# Wrong
class Constants:
    EOF = "\n"


# Correct
class EOLString:
    def __init__(self, src: str):
        self.origin = src

    def __str__(self) -> str:
        return self.origin + "\n"
```

- Stay away from class-level constants.

```python
# Bad
class Book:
    BOOK_NOT_FOUND = "book not found"

    def print(self):
        if {book not found}:
            raise Exception(
                self.BOOK_NOT_FOUND
            )

    def sell(self):
        if {book not found}:
            raise Exception(
                self.BOOK_NOT_FOUND
            )

# Good 1
class Book:
    def print(self):
        if {book not found}:
            raise Exception(
                "book not found, can’t print it"
            )

    def sell(self):
        if {book not found}:
            raise Exception(
                "book not found, can’t sell it"
            )

# Good 2
class Book:
    def print(self):
        x = self._find()

    def sell(self):
        x = self._find()

    def _find(self) -> X:
        if {book not found}:
            raise Exception(
                "book not found"
            )
        return "the book found"
```
---
## 9. Exceptions and Fail-Fast
### 9.1 Fail-Fast
- Always follow the fail-fast approach.
- Throw an exception in any suspicious situation.
- When something is not found, do one of the following: throw an exception; return a collection (possibly empty); return a Null Object.

```python
class NullUser(User):
    def __init__(self, name: str):
        self.label = name

    def name(self) -> str:
        return self.label

    def boost(self, salary: Cash):
        raise IllegalStateException("You can’t raise my salary")
```

- Never accept None as an argument.
- Instead of None, create a Null Object implementation.

```python
class Mask(ABC):
    @abstractmethod
    def matches(self, f: File) -> bool:
        pass


class AnyFile(Mask):
    def matches(self, f: File) -> bool:
        return True
```
### 9.2 Exception Handling
- Every except statement must have a very strong reason to exist.
- Always Chain Exceptions.

```python
def length(self, f: File) -> int:
    try:
        return os.path.getsize(PathOf(f))
    except FileNotFoundError as e:
        raise Exception("Can’t calculate file length.") from e
```

- Recover only once, at the highest level (the application entry point).
- All raised exceptions should be of the same type (Exception).
### 9.3 Validation
- Input validation and assertions should be implemented through decorators (wrappers), not inside core logic.

```python
class Day(ABC):
    @abstractmethod
    def distance_to(self, end: "Day") -> int:
        pass


class JdkDay(Day):
    def __init__(self, d: Date):
        self.date = d

    def distance_to(self, end: "Day") -> int:
        # assertion validation happens externally
        return LongAsInteger(end.date - self.date)


# Input validation decorator
class StrictDay(Day):
    def __init__(self, d: Day):
        self.origin = d

    def distance_to(self, end: Day) -> int:
        if end.compare_to(self) < 0:
            raise Exception(f"Start {self} must be earlier than end {end}")
        return self.origin.distance_to(end)


# Usage
day = StrictDay(JdkDay(Date()))
```

- Use Aspect-Oriented Programming to move supplementary mechanisms (like retries, logging, etc.) outside of core classes.

```python
from tenacity import retry, stop_after_attempt


class WebPage:
    @retry(stop=stop_after_attempt(3))
    def content(self) -> str:
        # fetch web page content
        pass
```
---
## 10. Composition over Inheritance
### 10.1 Class Structure
- A class should be final (all methods implemented) or abstract (no methods implemented, interface only).
- There is no place for inheritance.
### 10.2 Composition and Decorators
- Prefer composable decorators to build behavior step by step.

```python
names = Sorted(
    Unique(
        Capitalized(
            FileNames(
                Directory(
                    "/var/users/*.xml",
                ),
                "([^.]+)\\.xml",
            )
        )
    )
)
```

- Whenever you need to add new functionality to an existing class, create a new class or decorate an existing one.
- Modifying the original class should always be the last resort.
- Never use dependency injection.
- Use decorators (wrappers) for access control.

```python
car = SecureCar(Car("Mercedes-Benz SL63"), "admin")
```

- Use object composition instead of the MVC pattern.

```python
# Wrong
class Controller:
    def index(self) -> str:
        title = Model().title
        view = View()
        view.title = title
        return view.render_html()


# Good
Application(HttpGetBook(HtmlBook(MySQLBook("Elegant Objects")))).run()
```
### 10.3 Forbidden Patterns
- Never use the Singleton pattern.
