# Contributing to Agent-Score

First off, thanks for taking the time to contribute! ❤️

All types of contributions are encouraged and valued. See the [Table of Contents](#table-of-contents) for different ways to help and details about how this project handles them. Please make sure to read the relevant section before making your contribution. It will make it a lot easier for us maintainers and smooth out the experience for all involved.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [I Have a Question](#i-have-a-question)
- [I Want To Contribute](#i-want-to-contribute)
  - [Reporting Bugs](#reporting-bugs)
  - [Suggesting Enhancements](#suggesting-enhancements)
  - [Your First Code Contribution](#your-first-code-contribution)
  - [Pull Requests](#pull-requests)
- [Styleguides](#styleguides)
  - [Commit Messages](#commit-messages)
  - [Python Code Style](#python-code-style)
  - [Solidity Code Style](#solidity-code-style)
- [Join The Project Team](#join-the-project-team)

## Code of Conduct

This project and everyone participating in it is governed by the
[Agent-Score Code of Conduct](https://github.com/agent-score/agent-score/blob/main/CODE_OF_CONDUCT.md).
By participating, you are expected to uphold this code. Please report unacceptable behavior
to <conduct@agent-score.org>.

## I Have a Question

> If you want to ask a question, we assume that you have read the available [Documentation](https://docs.agent-score.org).

Before you ask a question, it is best to search for existing [Issues](https://github.com/agent-score/agent-score/issues) that might help you. In case you have found a suitable issue and still need clarification, you can write your question in this issue. It is also advisable to search the internet for answers first.

If you then still feel the need to ask a question and need clarification, we recommend the following:

- Open an [Issue](https://github.com/agent-score/agent-score/issues/new).
- Provide as much context as you can about what you're running into.
- Provide project and platform versions (Python, Solidity, Foundry, etc.), depending on what seems relevant.

We will then take care of the issue as soon as possible.

## I Want To Contribute

> ### Legal Notice
> When contributing to this project, you must agree that you have authored 100% of the content, that you have the necessary rights to the content and that the content you contribute may be provided under the project license.

### Reporting Bugs

#### Before Submitting a Bug Report

A good bug report shouldn't leave others needing to chase you up for more information. Therefore, we ask you to investigate carefully, collect information and describe the issue in detail in your report. Please complete the following steps in advance to help us fix any potential bug as fast as possible.

- Make sure that you are using the latest version.
- Determine if your bug is really a bug and not an error on your side e.g. using incompatible environment components/versions (Make sure that you have read the [documentation](https://docs.agent-score.org). If you are looking for support, you might want to check [this section](#i-have-a-question)).
- To see if other users have experienced (and potentially already solved) the same issue you are having, check if there is not already a bug report existing for your bug or error in the [bug tracker](https://github.com/agent-score/agent-score/issues?q=label%3Abug).
- Also make sure to search the internet (including Stack Overflow) to see if users outside of the GitHub community have discussed the issue.
- Collect information about the bug:
  - Stack trace (Traceback)
  - OS, Platform and Version (Windows, Linux, macOS, x86, ARM)
  - Version of the interpreter, compiler, SDK, runtime environment, package manager, depending on what seems relevant.
  - Possibly your input and the output
  - Can you reliably reproduce the issue? And can you also reproduce it with older versions?

#### How Do I Submit a Good Bug Report?

> You must never report security related issues, vulnerabilities or bugs including sensitive information to the issue tracker, or elsewhere in public. Instead sensitive bugs must be sent by email to <security@agent-score.org>.

We use GitHub issues to track bugs and errors. If you run into an issue with the project:

- Open an [Issue](https://github.com/agent-score/agent-score/issues/new). (Since we can't be sure at this point whether it is a bug or not, we ask you not to talk about a bug yet and not to label the issue.)
- Explain the behavior you would expect and the actual behavior.
- Please provide as much context as possible and describe the *reproduction steps* that someone else can follow to recreate the issue on their own. This usually includes your code. For good bug reports you should isolate the problem and create a reduced test case.
- Provide the information you collected in the previous section.

Once it's filed:

- The project team will label the issue accordingly.
- A team member will try to reproduce the issue with your provided steps. If there are no reproduction steps or no obvious way to reproduce the issue, the team will ask you for those steps and mark the issue as `needs-repro`. Bugs with the `needs-repro` tag will not be addressed until they are reproduced.
- If the team is able to reproduce the issue, it will be marked `needs-fix`, as well as possibly other tags (such as `critical`), and the issue will be left to be [implemented by someone](#your-first-code-contribution).

### Suggesting Enhancements

This section guides you through submitting an enhancement suggestion for Agent-Score, **including completely new features and minor improvements to existing functionality**. Following these guidelines will help maintainers and the community to understand your suggestion and find related suggestions.

#### Before Submitting an Enhancement

- Make sure that you are using the latest version.
- Read the [documentation](https://docs.agent-score.org) carefully and find out if the functionality is already covered, maybe by an individual configuration.
- Perform a [search](https://github.com/agent-score/agent-score/issues) to see if the enhancement has already been suggested. If it has, add a comment to the existing issue instead of opening a new one.
- Find out whether your idea fits with the scope and aims of the project. It's up to you to make a strong case to convince the project's developers of the merits of this feature. Keep in mind that we want features that will be useful to the majority of our users and not just a small subset. If you're just targeting a minority of users, consider writing an add-on/plugin library.

#### How Do I Submit a Good Enhancement Suggestion?

Enhancement suggestions are tracked as [GitHub issues](https://github.com/agent-score/agent-score/issues).

- Use a **clear and descriptive title** for the issue to identify the suggestion.
- Provide a **step-by-step description of the suggested enhancement** in as many details as possible.
- **Describe the current behavior** and **explain which behavior you expected to see instead** and why. At this point you can also tell which alternatives do not work for you.
- You may want to **include screenshots and animated GIFs** which help you demonstrate the steps or point out the part which the suggestion is related to. You can use [LICEcap](https://www.cockos.com/licecap/) to record GIFs on macOS and Windows, and [byzanz](https://github.com/GNOME/byzanz) on Linux.
- **Explain why this enhancement would be useful** to most Agent-Score users. You may also want to point out the other projects that solved it better and which could serve as inspiration.

### Your First Code Contribution

#### Environment Setup

1. **Python Environment** (Python 3.7.17 required):
   ```bash
   # Clone the repository
   git clone https://github.com/agent-score/agent-score.git
   cd agent-score

   # Create virtual environment
   python3.7 -m venv venv
   source venv/bin/activate

   # Install dependencies
   pip install -e ".[dev]"
   ```

2. **Foundry Environment** (for Solidity contracts):
   ```bash
   # Install Foundry
   curl -L https://foundry.paradigm.xyz | bash
   foundryup

   # Install dependencies
   forge install
   ```

3. **Run Tests**:
   ```bash
   # Python tests
   PYTHONPATH=src/credit-engine:src/a2a-middleware:demos/mvp:demos/minimal:demos/http python3 -m unittest discover -s src/credit-engine/tests -v
   PYTHONPATH=src/credit-engine:src/a2a-middleware:demos/mvp:demos/minimal:demos/http python3 -m unittest discover -s src/a2a-middleware/tests -v

   # Solidity tests
   forge test
   ```

#### Development Workflow

1. Fork the repository and create your branch from `main`.
2. Make your changes.
3. Add tests for your changes.
4. Ensure all tests pass.
5. Update documentation if needed.
6. Submit a pull request.

### Pull Requests

The process described here has several goals:

- Maintain Agent-Score's quality
- Fix problems that are important to users
- Engage the community in working toward the best possible Agent-Score
- Enable a sustainable system for Agent-Score's maintainers to review contributions

Please follow these steps to have your contribution considered by the maintainers:

1. Follow all instructions in [the template](.github/PULL_REQUEST_TEMPLATE.md)
2. Follow the [styleguides](#styleguides)
3. After you submit your pull request, verify that all [status checks](https://help.github.com/articles/about-status-checks/) are passing.
   - If a status check is failing, and you believe that the failure is unrelated to your change, please leave a comment on the pull request explaining why you believe it is unrelated. A maintainer will re-run the status check for you.
4. The pull request will be reviewed by at least one maintainer.
5. Once approved, the pull request will be merged.

## Styleguides

### Commit Messages

We follow the [Conventional Commits](https://www.conventionalcommits.org/) specification:

```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation only changes
- `style`: Changes that do not affect the meaning of the code (white-space, formatting, etc.)
- `refactor`: A code change that neither fixes a bug nor adds a feature
- `perf`: A code change that improves performance
- `test`: Adding missing tests or correcting existing tests
- `chore`: Changes to the build process or auxiliary tools

**Examples:**
```
feat(credit-engine): add device binding dimension to scoring model
fix(middleware): correct tier comparison direction in handshake
docs(whitepaper): update security analysis chapter
test(scoring): add device score improvement test case
```

### Python Code Style

- Follow [PEP 8](https://www.python.org/dev/peps/pep-0008/)
- Use type hints for all function signatures
- Use dataclasses for data models
- Maximum line length: 100 characters
- Docstrings: Google style

**Example:**
```python
from dataclasses import dataclass
from typing import Optional

@dataclass(frozen=True)
class AgentCard:
    """Agent identity and credit information.

    Attributes:
        name: Human-readable agent name
        did: Decentralized identifier
        credit_vc: Verifiable credential containing credit score
    """
    name: str
    did: str
    credit_vc: dict
    device_binding_vc: Optional[dict] = None

    def to_a2a_dict(self) -> dict:
        """Convert to A2A protocol format.

        Returns:
            Dictionary compatible with A2A x-agent-score extension
        """
        return {
            "name": self.name,
            "version": self.version,
            "x-agent-score": {
                "did": self.did,
                "credit_vc": self.credit_vc,
            },
        }
```

### Solidity Code Style

- Follow [Solidity Style Guide](https://docs.soliditylang.org/en/latest/style-guide.html)
- Use NatSpec comments for all public functions
- Maximum line length: 120 characters
- Contract and library names: PascalCase
- Function and variable names: camelCase
- Constants: UPPER_SNAKE_CASE

**Example:**
```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

/**
 * @title IdentityRegistry
 * @notice Registers agent identities and associates them with principals
 * @dev Compatible with ERC-8004 standard
 */
contract IdentityRegistry {
    uint256 public constant MAX_AGENTS_PER_PRINCIPAL = 100;

    /**
     * @notice Registers a new agent
     * @param agent Agent address
     * @param did Agent DID string
     * @param principalDid Principal DID string
     * @param metadataURI URI for agent metadata
     * @return agentId Unique agent identifier
     */
    function registerAgent(
        address agent,
        string memory did,
        string memory principalDid,
        string memory metadataURI
    ) external returns (uint256 agentId) {
        // Implementation
    }
}
```

## Join The Project Team

If you're interested in becoming a core contributor, please reach out to us at <team@agent-score.org> with your background and areas of interest. We're always looking for talented individuals to join our team!

## Attribution

This guide is based on the [contributing-gen](https://github.com/bttger/contributing-gen) project.
