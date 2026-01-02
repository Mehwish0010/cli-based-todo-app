# Advanced Todo Application

> A smart habit tracker with auto-rescheduling for recurring tasks

[![Python 3.13](https://img.shields.io/badge/python-3.13-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Tests](https://img.shields.io/badge/tests-40%2F41%20passing-green.svg)](todo-app/test_all_features.py)

## Overview

Advanced Todo Application is a Python CLI tool that automatically reschedules recurring tasks when you complete them. Perfect for tracking daily habits, weekly meetings, monthly bills, or any task that repeats on a schedule - without manually recreating them each time.

### Key Features

- **🔄 Smart Recurring Tasks**: Daily, weekly (Mon/Wed/Fri), monthly (1st, 15th, last day)
- **✨ Auto-Rescheduling**: Complete a task → Next occurrence automatically created
- **🎯 State Management**: Track lifecycle (Pending → Active → Completed/Snoozed/Cancelled)
- **📅 Edge Case Handling**: Smart date handling (Jan 31 → Feb 28 for monthly tasks)
- **⚡ Due Dates**: Set deadlines and track upcoming/overdue tasks
- **🧪 Deterministic Testing**: TimeProvider pattern for reproducible behavior

## Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/YOUR_USERNAME/advanced-todo-app.git
cd advanced-todo-app/todo-app

# No external dependencies needed - uses Python standard library only!
```

### Run the Demo

```bash
# See all features in action
python main.py

# Interactive CLI for testing CRUD operations
python cli.py

# Experiment with different recurrence patterns
python experiment.py

# Run comprehensive test suite (40/41 tests)
python test_all_features.py
```

## Usage Examples

### Create Daily Recurring Task

```python
from datetime import date
from src.todo_app.models.task import Task
from src.todo_app.storage.todo_store import TodoStore

store = TodoStore()

# Create a daily task
task = Task(
    title="Take vitamins",
    recurrence_rule={"freq": "DAILY", "interval": 1},
    due_date=date.today()
)
store.add_task(task)
```

### Weekly Task (Multiple Days)

```python
# Team meeting every Monday and Wednesday
task = Task(
    title="Team standup",
    recurrence_rule={
        "freq": "WEEKLY",
        "interval": 1,
        "byday": [0, 2]  # 0=Monday, 2=Wednesday
    }
)
```

### Monthly Task with Edge Case Handling

```python
# Pay rent on the 1st of each month
task = Task(
    title="Pay rent",
    recurrence_rule={
        "freq": "MONTHLY",
        "interval": 1,
        "bymonthday": 1
    }
)

# Task on Jan 31 automatically adjusts to Feb 28 (or 29 in leap years)
task_end_month = Task(
    title="Monthly report",
    recurrence_rule={
        "freq": "MONTHLY",
        "interval": 1,
        "bymonthday": "LAST"  # Last day of month
    }
)
```

### Complete and Auto-Reschedule

```python
from src.todo_app.services.time_provider import SystemTimeProvider
from src.todo_app.services.state_manager import transition_task_state
from src.todo_app.services.recurrence import create_next_occurrence
from src.todo_app.models.task import TaskState

time_provider = SystemTimeProvider()

# Complete the task
transition_task_state(task, TaskState.ACTIVE, time_provider)
transition_task_state(task, TaskState.COMPLETED, time_provider)

# Automatically create next occurrence
next_task = create_next_occurrence(task, date.today(), 1)
store.add_task(next_task)  # Tomorrow's task is ready!
```

## Architecture

### Core Principles

1. **Spec-Driven Development**: All features defined in specifications before code generation
2. **Deterministic Behavior**: TimeProvider injection for reproducible testing
3. **Explicit State Machine**: VALID_TRANSITIONS map prevents invalid state changes
4. **Time-Aware Logic**: UTC storage, local display, edge case handling
5. **Data-Driven Recurrence**: RecurrenceRule stored as dict, not code
6. **Extensibility**: Ready for database, multi-user, AI integration

### Project Structure

```
todo-app/
├── src/todo_app/
│   ├── models/
│   │   └── task.py              # Task entity, TaskState enum, validation
│   ├── services/
│   │   ├── time_provider.py     # TimeProvider pattern (System, Test)
│   │   ├── state_manager.py     # State transitions, validation
│   │   └── recurrence.py        # Daily/weekly/monthly logic
│   └── storage/
│       └── todo_store.py        # In-memory storage (dict-based)
├── tests/
│   ├── unit/                    # Unit tests (future)
│   ├── integration/             # Integration tests (future)
│   └── api/                     # API tests (future)
├── main.py                      # Demo application (7 scenarios)
├── cli.py                       # Interactive CLI (CRUD operations)
├── experiment.py                # Feature experimentation
└── test_all_features.py         # Comprehensive test suite (41 tests)
```

### State Machine

```
PENDING ──┬──> ACTIVE ──┬──> COMPLETED
          │             ├──> SNOOZED ──> PENDING
          │             └──> CANCELLED
          └──> CANCELLED
```

### Recurrence Patterns

| Pattern | Example | Next Occurrence Logic |
|---------|---------|----------------------|
| Daily | Every day | `current_date + interval days` |
| Daily (interval) | Every 3 days | `current_date + 3 days` |
| Weekly | Mon/Wed/Fri | Next weekday in sequence |
| Bi-weekly | Every 2 weeks on Tuesday | `current_date + 14 days` |
| Monthly | 15th of month | `next_month, day=15` |
| Monthly (edge) | 31st → Feb 28/29 | `min(31, days_in_month)` |
| Monthly (last) | Last day of month | `last_day_of_next_month` |

## Testing

### Run All Tests

```bash
cd todo-app
python test_all_features.py
```

**Test Coverage** (40/41 passing - 97.6%):
- ✅ Basic task operations (5/5)
- ✅ State transitions (6/6)
- ✅ Daily recurrence (3/3)
- ✅ Weekly recurrence (4/4)
- ✅ Monthly recurrence (6/6)
- ✅ End conditions (2/3)
- ✅ Time provider (3/3)
- ✅ Storage operations (4/4)
- ✅ Validation (5/5)
- ✅ Complete workflows (2/2)

### Interactive Testing

```bash
# Test create, update, delete yourself
python cli.py
```

## Development

### Requirements

- Python 3.13+
- No external dependencies (uses standard library only)

### Running the Demo

```bash
python main.py
```

**Demo Output**:
- Test 1: Daily recurring task creation
- Test 2: Complete and auto-reschedule
- Test 3: Weekly task (multiple days)
- Test 4: Monthly task
- Test 5: List all tasks
- Test 6: Edge case (Feb 31 → 28)
- Test 7: State transitions (PENDING → ACTIVE → SNOOZED → auto-transition)

### Code Standards

- Constitutional principles enforced (see `.specify/memory/constitution.md`)
- All code generated by Claude Code (no manual coding)
- Spec-first development workflow
- Deterministic testing via TimeProvider pattern

## Contributing

We follow **Spec-Driven Development (SDD)** methodology. See [CONTRIBUTING.md](CONTRIBUTING.md) for:
- Branch naming conventions (`###-feature-name`)
- Specification → Plan → Tasks → Implementation workflow
- Pull request process
- Code generation guidelines

## Roadmap

### Current (Phase II - Advanced Features)
- ✅ Recurring tasks (daily/weekly/monthly)
- ✅ Due dates and time awareness
- ✅ State management
- ✅ Auto-rescheduling
- ✅ Edge case handling

### Future (Phase III - Cloud Native)
- [ ] Persistent storage (PostgreSQL/MongoDB)
- [ ] REST API (Flask/FastAPI)
- [ ] Web interface
- [ ] Multi-user support
- [ ] Kubernetes deployment

### Future (Phase IV - AI Integration)
- [ ] Natural language task creation
- [ ] AI chatbot interface
- [ ] Smart scheduling suggestions
- [ ] OpenAI Agents SDK integration

## License

[MIT License](LICENSE) - Open source and free to use

## Acknowledgments

Built with [Claude Code](https://claude.com/claude-code) following Spec-Driven Development methodology.

**Project Structure**:
- `specs/` - Feature specifications
- `history/` - Prompt History Records (PHR)
- `.specify/` - SDD templates and scripts

## Support

- **Issues**: Report bugs or request features via [GitHub Issues](https://github.com/YOUR_USERNAME/advanced-todo-app/issues)
- **Documentation**: See `specs/` directory for detailed feature specifications
- **Architecture**: See `.specify/memory/constitution.md` for design principles

---

**Made with ❤️ using Spec-Driven Development**
