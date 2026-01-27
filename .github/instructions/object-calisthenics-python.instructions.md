---
applyTo: "**/*.py"
---

# Object Calisthenics — Copilot Instructions

These instructions define a *design philosophy* for writing maintainable, testable, and readable Python. They complement (not replace) the repo’s coding style rules. Examples follow PEP 8 formatting.

## How To Apply These Rules
- Treat these as constraints for everyday coding, not absolutes.
- If a rule conflicts with a hard requirement (performance, framework constraints, public API compatibility), follow the requirement and document the tradeoff.
- When in doubt: optimize for **cohesion**, **local reasoning**, and **testability**.

---

## The 9 Object Calisthenics Rules

### 1) One Level Of Indentation Per Function/Method
- Avoid deep nesting in functions.
- Prefer:
  - guard clauses (early `return` / `raise`),
  - extracting small helper functions,
  - moving branching behavior into objects.
- Target: most functions have **0–1** indentation level (loops/ifs inside helper methods are fine if contained).

Why: reduces cognitive load and hidden bugs in nested logic.

#### Examples:

**Bad**
```python
def ship_order(order, gateway) -> None:
    if order is not None:
        if order.is_paid:
            if not order.is_shipped:
                if gateway.can_ship(order.address):
                    gateway.create_shipment(order)
                else:
                    raise ValueError("Unsupported address")
```

**Good**
```python
def ship_order(order, gateway) -> None:
    if order is None:
        raise ValueError("Missing order")
    if not order.is_paid:
        raise ValueError("Order not paid")
    if order.is_shipped:
        return

    ensure_can_ship(order, gateway)
    gateway.create_shipment(order)


def ensure_can_ship(order, gateway) -> None:
    if not gateway.can_ship(order.address):
        raise ValueError("Unsupported address")
```

### 2) Don’t Use `else`
- Prefer guard clauses:
  - handle error/edge cases first, then proceed with the “happy path”.
- Alternatives to `if/else` chains:
  - polymorphism (different classes implementing the same interface),
  - strategy/state objects,
  - dispatch tables (`dict[key] -> handler`),
  - `match`/`case` where it improves readability.
- If `else` is the clearest option for a tiny expression, keep it small and consider a conditional expression (`x = a if cond else b`).

Why: keeps the happy path flat and easier to follow.

#### Examples:

**Bad**
```python
def login(username: str, password: str, repo) -> str:
    if repo.is_valid(username, password):
        return "/home"
    else:
        return "/login?error=bad-credentials"
```

**Good**
```python
def login(username: str, password: str, repo) -> str:
    if not repo.is_valid(username, password):
        return "/login?error=bad-credentials"
    return "/home"
```

### 3) Wrap Primitives And Strings
- Avoid “primitive obsession” for domain concepts.
- When a primitive has rules/behavior (validation, formatting, arithmetic, parsing), represent it as a **value object**, e.g.:
  - `EmailAddress`, `Money`, `Percent`, `OrderId`, `UtcTimestamp`.
- Prefer `@dataclass(frozen=True)` for value objects.
- Keep wrappers lightweight; don’t wrap primitives that are truly incidental.

Why: centralizes validation and behavior in one place.

#### Examples:

**Bad**
```python
def send_receipt(email: str, mailer) -> None:
    if "@" not in email:
        raise ValueError("Invalid email")
    mailer.send(to=email.strip().lower(), template="receipt")
```

**Good**
```python
from dataclasses import dataclass


@dataclass(frozen=True)
class EmailAddress:
    value: str

    def __post_init__(self) -> None:
        normalized = self.value.strip().lower()
        if "@" not in normalized:
            raise ValueError("Invalid email")
        object.__setattr__(self, "value", normalized)


def send_receipt(email: EmailAddress, mailer) -> None:
    mailer.send(to=email.value, template="receipt")
```

### 4) First-Class Collections
- If a class’s primary responsibility is operating on a collection, wrap it:
  - `Users`, `LineItems`, `Permissions`, `Schedule`.
- Prefer: one collection field + behaviors that belong with it (filtering, validation, domain rules).
- Avoid scattering list/dict manipulation logic across multiple modules.

Why: gives collection rules a single, cohesive home.

#### Examples:

**Bad**
```python
def total(items) -> int:
    return sum(i.price_cents * i.quantity for i in items)


def has_duplicates(items) -> bool:
    return len({i.sku for i in items}) != len(items)
```

**Good**
```python
class LineItems:
    def __init__(self, items: list) -> None:
        self._items = list(items)

    def total_cents(self) -> int:
        return sum(i.price_cents * i.quantity for i in self._items)

    def ensure_no_duplicates(self) -> None:
        skus = [i.sku for i in self._items]
        if len(set(skus)) != len(skus):
            raise ValueError("Duplicate line items")
```

### 5) One Dot Per Line (Limit Chaining)
- Avoid long call chains like `a.b().c.d().e()` that reach through multiple objects.
- Prefer:
  - naming intermediate results,
  - moving behavior onto the object you’re navigating to,
  - providing intention-revealing methods.
- Fluent APIs (e.g., query builders) are the main exception.

Why: reduces coupling and Law of Demeter violations.

#### Examples:

**Bad**
```python
def display_city(request) -> str:
    return request.user.profile.address.city.strip().upper()
```

**Good**
```python
def display_city(request) -> str:
    user = request.user
    return user.display_city()


class User:
    def display_city(self) -> str:
        city = self.profile.address.city
        return city.strip().upper()
```

### 6) Don’t Abbreviate
- Choose names that communicate intent without needing extra comments.
- Abbreviations hide meaning and encourage reuse-by-copy.
- If a name feels “too long”, it’s often a design smell (method/class doing too much).

Why: improves readability and exposes overgrown responsibilities.

#### Examples:

**Bad**
```python
def calc_tot_amt(usr, invs) -> int:
    return sum(inv.amt for inv in invs if inv.uid == usr.id)
```

**Good**
```python
def calculate_total_amount_for_user(user, invoices) -> int:
    return sum(invoice.amount for invoice in invoices if invoice.user_id == user.id)
```

### 7) Keep Entities Small
- Prefer small:
  - functions with a single responsibility,
  - classes that fit in your head,
  - modules that can be navigated quickly.
- Practical guidelines (adapt to the repo):
  - functions: usually ≤ ~20–40 logical lines,
  - classes: usually ≤ ~150 lines,
  - modules: split when they become “grab bag” utilities.

Why: small units are easier to test, read, and change.

#### Examples:

**Bad**
```python
def export_report(path: str, rows: list[dict]) -> None:
    # parse + validate + compute + write, all mixed together
    cleaned = []
    for row in rows:
        if "amount" in row and row["amount"] is not None:
            cleaned.append(int(row["amount"]))
    total = sum(cleaned)
    with open(path, "w", encoding="utf-8") as f:
        f.write(str(total))
```

**Good**
```python
def parse_amounts(rows: list[dict]) -> list[int]:
    return [int(r["amount"]) for r in rows if r.get("amount") is not None]


def compute_total(amounts: list[int]) -> int:
    return sum(amounts)


def write_text(path: str, text: str) -> None:
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)
```

### 8) No Classes With More Than Two Instance Variables
- Use this as a forcing function for cohesion:
  - split responsibilities,
  - compose objects,
  - wrap primitives (Rule 3) and collections (Rule 4).
- This rule is aspirational; if violated, do so intentionally and keep the class conceptually simple.

Why: encourages composition and high cohesion.

#### Examples:

**Bad**
```python
class Order:
    def __init__(
        self,
        order_id,
        user_id,
        shipping_address,
        billing_address,
        items,
        total_cents,
    ):
        self.order_id = order_id
        self.user_id = user_id
        self.shipping_address = shipping_address
        self.billing_address = billing_address
        self.items = items
        self.total_cents = total_cents
```

**Good**
```python
from dataclasses import dataclass


@dataclass(frozen=True)
class OrderId:
    value: str


@dataclass
class Order:
    order_id: OrderId
    checkout: "Checkout"


@dataclass
class Checkout:
    items: "LineItems"
    shipping: "ShippingDetails"
```

### 9) No Getters/Setters/Properties (Tell, Don’t Ask)
- Prefer behavior methods over exposing state for external decision-making.
  - Instead of: `if user.is_active: ...` scattered everywhere,
  - Prefer: `user.ensure_can_login()` or `user.can_login()` used at the boundary.
- In Python, *read-only* properties can be fine when they are:
  - derived from internal state,
  - cheap,
  - side-effect-free.
- Avoid “anemic models” where objects only hold data and all logic lives elsewhere.

Why: keeps decisions with the data they depend on.

#### Examples:

**Bad**
```python
def pay(invoice, amount_cents: int) -> None:
    if invoice.status == "PAID":
        raise ValueError("Already paid")
    invoice.status = "PAID"
    invoice.paid_amount_cents = amount_cents
```

**Good**
```python
class Invoice:
    def pay(self, amount_cents: int) -> None:
        if self._status == "PAID":
            raise ValueError("Already paid")
        self._status = "PAID"
        self._paid_amount_cents = amount_cents
```

---

## Additional Principles (To Keep The Rules Practical)

### Encapsulation By Default
- Treat leading-underscore attributes as private.
- Avoid returning mutable internals; expose intention-revealing operations instead.

Why: protects invariants and prevents accidental mutation.

#### Examples:

**Bad**
```python
class Bag:
    def __init__(self) -> None:
        self.items: list[str] = []


bag = Bag()
bag.items.append("surprise")
```

**Good**
```python
class Bag:
    def __init__(self) -> None:
        self._items: list[str] = []

    def add(self, item: str) -> None:
        self._items.append(item)

    def items(self) -> tuple[str, ...]:
        return tuple(self._items)
```

### Push Decisions Down
- Put business rules close to the data they govern.
- Prefer moving logic into:
  - value objects,
  - collection wrappers,
  - domain entities.

Why: removes duplication and keeps rules close to data.

#### Examples:

**Bad**
```python
def can_refund(order) -> bool:
    return order.status == "PAID" and not order.is_shipped
```

**Good**
```python
class Order:
    def can_refund(self) -> bool:
        return self._status == "PAID" and not self._is_shipped
```

### Prefer Composition
- Compose small objects instead of building inheritance trees.
- If inheritance is necessary, keep base classes tiny and behavior-focused.

Why: composition is more flexible and testable than inheritance.

#### Examples:

**Bad**
```python
class CsvReportExporter:
    def export(self, report) -> str:
        ...


class WeeklyCsvReportExporter(CsvReportExporter):
    def export(self, report) -> str:
        ...
```

**Good**
```python
class ReportFormatter:
    def format(self, report) -> str:
        ...


class ReportExporter:
    def __init__(self, formatter: ReportFormatter) -> None:
        self._formatter = formatter

    def export(self, report) -> str:
        return self._formatter.format(report)
```

### Make Side Effects Explicit
- Keep pure logic separate from I/O (filesystem, network, DB).
- Prefer dependency injection (pass collaborators in) for testability.

Why: makes behavior testable without touching external systems.

#### Examples:

**Bad**
```python
def calculate_and_persist_total(repo, user_id: str) -> int:
    total = sum(r.amount for r in repo.fetch_rows(user_id))
    repo.save_total(user_id, total)
    return total
```

**Good**
```python
def calculate_total(rows) -> int:
    return sum(r.amount for r in rows)


def persist_total(repo, user_id: str, total: int) -> None:
    repo.save_total(user_id, total)
```

---

## What Copilot Should Do
- When generating code, actively try to:
  - reduce nesting,
  - remove `else` via guard clauses,
  - introduce value objects for domain primitives,
  - wrap collections that have domain behavior,
  - shorten chains and improve encapsulation,
  - replace “get then decide elsewhere” with “tell the object to do it”.
- Apply the **Additional Principles** by default (encapsulation, push decisions down, composition, explicit side effects), unless a requirement justifies an exception.
- If applying a rule would distort clarity or add ceremony, keep the simpler solution and note the tradeoff in a short comment/docstring.

---

## References
- https://williamdurand.fr/2013/06/03/object-calisthenics/
- https://peps.python.org/pep-0008/
- https://en.wikipedia.org/wiki/Law_of_Demeter
