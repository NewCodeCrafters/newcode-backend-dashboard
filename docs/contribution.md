# Contributing to NCC Dashboard

Thank you for your interest in contributing to the NCC Dashboard project! We welcome contributions from the community and appreciate your effort to improve this project.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Workflow](#development-workflow)
- [Coding Standards](#coding-standards)
- [Commit Guidelines](#commit-guidelines)
- [Pull Request Process](#pull-request-process)
- [Testing Guidelines](#testing-guidelines)
- [Documentation](#documentation)
- [Reporting Bugs](#reporting-bugs)
- [Requesting Features](#requesting-features)
- [Questions](#questions)

## Code of Conduct

By participating in this project, you agree to maintain a respectful and inclusive environment. We expect all contributors to:

- Be respectful and considerate in communication
- Welcome newcomers and help them get started
- Accept constructive criticism gracefully
- Focus on what is best for the community
- Show empathy towards other community members

## Getting Started

### Prerequisites

Before you begin contributing, ensure you have:

- Python 3.8 or higher installed
- Git installed and configured
- Basic understanding of Django framework
- Familiarity with Poetry for dependency management

### Setting Up Development Environment

1. **Fork the repository** on GitHub

2. **Clone your fork** locally:
   ```bash
   git clone https://github.com/your-username/ncc-dashboard-bc.git
   cd ncc-dashboard-bc
   ```

3. **Add upstream remote**:
   ```bash
   git remote add upstream https://github.com/original-owner/ncc-dashboard-bc.git
   ```

4. **Create and activate virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On macOS/Linux
   venv\Scripts\activate     # On Windows
   ```

5. **Install Poetry and dependencies**:
   ```bash
   pip install -r requirements.txt
   poetry install --no-root
   ```

6. **Set up environment variables**:
   ```bash
   cp .env.example .env
   # Edit .env with your local configuration
   ```

7. **Run migrations**:
   ```bash
   python manage.py migrate --settings=core.settings.dev
   ```

8. **Create a superuser** (optional):
   ```bash
   python manage.py createsuperuser --settings=core.settings.dev
   ```

9. **Run the development server**:
   ```bash
   python manage.py runserver --settings=core.settings.dev
   ```

## Development Workflow

### Branching Strategy

We follow a feature branch workflow:

- `main` - Production-ready code
- `develop` - Integration branch for features
- `feature/*` - New features
- `bugfix/*` - Bug fixes
- `hotfix/*` - Urgent production fixes

### Creating a Feature Branch

1. **Ensure your main branch is up to date**:
   ```bash
   git checkout main
   git pull upstream main
   ```

2. **Create a new feature branch**:
   ```bash
   git checkout -b feature/your-feature-name
   ```

3. **Make your changes** and commit regularly

4. **Keep your branch updated** with main:
   ```bash
   git fetch upstream
   git rebase upstream/main
   ```

## Coding Standards

### Python Style Guide

We follow PEP 8 with some modifications. Please ensure your code adheres to these standards:

- Use 4 spaces for indentation (no tabs)
- Maximum line length: 120 characters
- Use meaningful variable and function names
- Add docstrings to all functions, classes, and modules
- Use type hints where appropriate

### Django Best Practices

- Follow Django's coding style and conventions
- Keep views thin, models fat
- Use Django's built-in features before writing custom code
- Write reusable and modular code
- Use class-based views where appropriate
- Keep URL patterns organized and well-named

### Code Formatting

We use the following tools for code quality:

**Black** for code formatting:
```bash
poetry run black .
```

**Flake8** for linting:
```bash
poetry run flake8 .
```

**isort** for import sorting:
```bash
poetry run isort .
```

**Run all formatting tools before committing**:
```bash
poetry run black . && poetry run isort . && poetry run flake8 .
```

### File Organization

- Place new apps in the `apps/` directory
- Keep related functionality together
- Use descriptive file and directory names
- Organize imports: standard library, third-party, local imports

### Naming Conventions

- **Classes**: Use PascalCase (e.g., `StudentModel`, `BatchView`)
- **Functions/Methods**: Use snake_case (e.g., `get_student_data`, `calculate_score`)
- **Constants**: Use UPPER_SNAKE_CASE (e.g., `MAX_BATCH_SIZE`, `DEFAULT_TIMEOUT`)
- **Variables**: Use snake_case (e.g., `student_name`, `batch_count`)

## Commit Guidelines

### Commit Message Format

We follow the Conventional Commits specification:

```
<type>(<scope>): <subject>

<body>

<footer>
```

#### Types

- `feat`: A new feature
- `fix`: A bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, missing semicolons, etc.)
- `refactor`: Code refactoring without changing functionality
- `perf`: Performance improvements
- `test`: Adding or updating tests
- `chore`: Maintenance tasks, dependency updates
- `ci`: CI/CD configuration changes

#### Examples

```bash
feat(student): add bulk import functionality

- Implemented CSV import for student data
- Added validation for imported records
- Created progress indicator for large imports

Closes #123
```

```bash
fix(batch): resolve duplicate enrollment issue

Fixed a bug where students could be enrolled in the same batch multiple times.

Fixes #456
```

```bash
docs(readme): update installation instructions

Updated Python version requirements and clarified Poetry setup steps.
```

### Commit Best Practices

- Write clear, concise commit messages
- Use the present tense ("add feature" not "added feature")
- Use the imperative mood ("move cursor to..." not "moves cursor to...")
- Keep the subject line under 50 characters
- Separate subject from body with a blank line
- Reference issues and pull requests when relevant
- Make atomic commits (one logical change per commit)

## Pull Request Process

### Before Submitting

1. **Update your branch** with the latest changes from main:
   ```bash
   git fetch upstream
   git rebase upstream/main
   ```

2. **Run tests** to ensure everything passes:
   ```bash
   python manage.py test --settings=core.settings.dev
   ```

3. **Run code quality checks**:
   ```bash
   poetry run black . && poetry run isort . && poetry run flake8 .
   ```

4. **Update documentation** if you've changed functionality

5. **Add tests** for new features or bug fixes

### Submitting a Pull Request

1. **Push your branch** to your fork:
   ```bash
   git push origin feature/your-feature-name
   ```

2. **Create a Pull Request** on GitHub from your fork to the main repository

3. **Fill out the PR template** with:
   - Clear description of changes
   - Related issue numbers
   - Screenshots (if UI changes)
   - Testing steps
   - Checklist completion

4. **Respond to feedback** from reviewers promptly

5. **Keep your PR updated** by rebasing if main branch changes

### Pull Request Template

When creating a PR, include:

```markdown
## Description
Brief description of what this PR does

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Related Issues
Closes #(issue number)

## How Has This Been Tested?
Describe the tests you ran and their results

## Screenshots (if applicable)
Add screenshots for UI changes

## Checklist
- [ ] My code follows the project's style guidelines
- [ ] I have performed a self-review of my code
- [ ] I have commented my code where necessary
- [ ] I have updated the documentation
- [ ] My changes generate no new warnings
- [ ] I have added tests that prove my fix/feature works
- [ ] New and existing tests pass locally
- [ ] Any dependent changes have been merged
```

### Review Process

- At least one maintainer must approve your PR
- All CI checks must pass
- No unresolved conversations
- Code must meet quality standards
- Tests must have adequate coverage

## Testing Guidelines

### Writing Tests

- Write tests for all new features and bug fixes
- Place tests in the appropriate app's `tests.py` or `tests/` directory
- Use Django's TestCase or TransactionTestCase
- Follow the Arrange-Act-Assert pattern

### Test Structure

```python
from django.test import TestCase
from apps.student.models import Student

class StudentModelTestCase(TestCase):
    """Test cases for Student model"""
    
    def setUp(self):
        """Set up test data"""
        self.student = Student.objects.create(
            name="John Doe",
            email="john@example.com"
        )
    
    def test_student_creation(self):
        """Test that a student can be created"""
        self.assertEqual(self.student.name, "John Doe")
        self.assertEqual(self.student.email, "john@example.com")
    
    def test_student_str_representation(self):
        """Test the string representation of student"""
        self.assertEqual(str(self.student), "John Doe")
```

### Running Tests

Run all tests:
```bash
python manage.py test --settings=core.settings.dev
```

Run tests for a specific app:
```bash
python manage.py test apps.student --settings=core.settings.dev
```

Run with coverage:
```bash
poetry run coverage run --source='.' manage.py test --settings=core.settings.dev
poetry run coverage report
poetry run coverage html  # Generate HTML coverage report
```

### Test Coverage

- Aim for at least 80% code coverage
- Focus on testing critical functionality
- Include edge cases and error conditions
- Test both success and failure scenarios

## Documentation

### Code Documentation

- Add docstrings to all modules, classes, and functions
- Use clear and descriptive comments for complex logic
- Update docstrings when changing functionality

### Docstring Format

```python
def calculate_student_average(student_id, subject=None):
    """
    Calculate the average score for a student.
    
    Args:
        student_id (int): The ID of the student
        subject (str, optional): Filter by specific subject. Defaults to None.
    
    Returns:
        float: The average score, or None if no scores found
    
    Raises:
        Student.DoesNotExist: If the student ID is invalid
    
    Example:
        >>> calculate_student_average(123)
        85.5
        >>> calculate_student_average(123, subject="Mathematics")
        90.0
    """
    pass
```

### Project Documentation

- Update README.md for significant changes
- Document new features in separate docs if needed
- Keep API documentation up to date
- Add inline comments for complex algorithms

## Reporting Bugs

### Before Reporting

1. Check if the bug has already been reported in Issues
2. Verify the bug exists in the latest version
3. Try to reproduce the bug consistently
4. Gather relevant information about your environment

### Bug Report Template

When reporting a bug, include:

```markdown
**Bug Description**
A clear and concise description of the bug

**To Reproduce**
Steps to reproduce the behavior:
1. Go to '...'
2. Click on '...'
3. Scroll down to '...'
4. See error

**Expected Behavior**
What you expected to happen

**Screenshots**
If applicable, add screenshots

**Environment:**
 - OS: [e.g., Windows 10, Ubuntu 20.04]
 - Python Version: [e.g., 3.9.5]
 - Django Version: [e.g., 4.2]
 - Browser: [e.g., Chrome 91]

**Additional Context**
Any other relevant information
```

## Requesting Features

### Feature Request Template

```markdown
**Is your feature request related to a problem?**
A clear description of the problem

**Describe the solution you'd like**
A clear description of what you want to happen

**Describe alternatives you've considered**
Any alternative solutions or features you've considered

**Additional context**
Any other context, mockups, or examples
```

### Feature Discussion

- Open an issue to discuss major features before implementation
- Be open to feedback and alternative approaches
- Consider backward compatibility
- Think about maintenance and long-term impact

## Questions

If you have questions about contributing:

1. Check the README.md and documentation first
2. Search existing issues for similar questions
3. Open a new issue with the "question" label
4. Join our community chat (if available)

## Recognition

Contributors will be:
- Listed in the project's contributors section
- Mentioned in release notes for significant contributions
- Credited in the codebase where appropriate

## License

By contributing to this project, you agree that your contributions will be licensed under the same license as the project.

---

Thank you for contributing to NCC Dashboard! Your efforts help make this project better for everyone.