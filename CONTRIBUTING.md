# Contributing to QGIS Plugin Builder

Thanks for your interest in improving Plugin Builder! Bug reports, fixes,
documentation improvements, and new features are all welcome.

## Before you start

- **Bugs:** open an issue using the bug report form. Please search existing
  issues first.
- **Security vulnerabilities:** do **not** open a public issue. Follow
  [SECURITY.md](SECURITY.md) to report privately.
- **New features or larger changes:** open an issue to discuss the idea before
  writing code, so we can agree on the approach and you don't spend time on
  something that won't be merged.
- **Small fixes** (typos, docs, obvious bugs) can go straight to a pull request.

## Which branch?

| Plugin           | QGIS version | Branch    | Accepting               |
| ---------------- | ------------ | --------- | ----------------------- |
| Plugin Builder 4 | 4.x          | `QGIS4`   | Fixes and features      |
| Plugin Builder 3 | 3.x          | `QGIS3`   | Bug and security fixes  |
| Plugin Builder 2 | 2.x          | `LTR_2.x` | No longer maintained    |

Most pull requests should target `QGIS4`.

## Development setup

1. Fork the repository and create a branch from `QGIS4`.
2. Install QGIS 4 and a Python environment that can import `qgis`.
3. Install the development tools:

   ```bash
   pip install pytest-qgis pytest-cov ruff mypy pre-commit
   pre-commit install
   ```

4. Deploy the plugin locally for manual testing (requires `pb_tool`):

   ```bash
   make deploy
   ```

## Checks

Run these before opening a pull request. CI runs the test suite on every PR.

```bash
make test       # pytest (uses pytest-qgis)
make lint       # ruff check
make typecheck  # mypy, configured in mypy.ini
```

The pre-commit hooks also run `ruff format`, `bandit`, and basic file hygiene
checks on each commit.

## Code guidelines

- **Style** is enforced by ruff (line length 88). Let `ruff format` handle
  formatting.
- **Type hints** are expected on new and changed code in `pluginbuilder4/`,
  and mypy must pass.
- **Don't use `assert`** in plugin code. Bandit flags it, and that blocks
  uploads to plugins.qgis.org. Narrow types with an `if` check and `raise`
  instead.
- **Templates matter.** Code under `pluginbuilder4/plugin_templates/` is copied
  into every plugin that users generate. Keep it clean and well-commented, and
  test by generating a plugin and loading it in QGIS.
- **Add or update tests** for behavior changes.
- **Update the docs** in `help/` when you change user-facing behavior.

## Pull requests

- Keep each PR focused on one change. Unrelated fixes belong in separate PRs.
- Write a clear description: what changed, why, and how you tested it.
- Link the related issue (for example, `Fixes #123`).
- Fill in **every** section of the pull request template, including the AI
  assistance disclosure.

## AI assistance disclosure

AI tools (chat assistants, coding agents, autocomplete, and so on) may be used
to help with contributions. **Every pull request must declare whether and how
AI was used.** The pull request template has a section for this.

### What to declare

1. **Level of use**, choosing the closest option:
   - **None**: no AI tools were used.
   - **Minor**: autocomplete, small suggestions, help with wording, or
     explanations of existing code. You wrote the substance yourself.
   - **Substantial**: AI generated significant portions of the code, tests,
     or documentation, which you then reviewed and edited.
   - **Mostly generated**: most of the change was produced by AI, for example
     by a coding agent, with your guidance and review.
2. **Tools**: which tools and models you used (for example, "GitHub Copilot"
   or "Claude Code").
3. **Notes**: a sentence or two on what the AI did. For example: "Generated
   the initial test cases, which I then extended," or "Used to draft the
   docstrings."

### Your responsibilities

Whatever the level of AI use, **you are the author and are responsible for
the contribution.** That means:

- You have read and understand every line you submit, and you can explain and
  defend it in review.
- You have run the checks and tested the change yourself.
- You respond to review comments yourself. Please don't paste reviewer
  questions into an AI tool and post its answer unedited.
- You have the right to submit the code under this project's license (see
  [License](#license)).

Using AI doesn't count against a contribution. Not disclosing it does:
pull requests with missing or inaccurate disclosures may be closed.

## License

Plugin Builder is licensed under the
[GNU General Public License v2.0](LICENSE). By submitting a contribution, you
agree that it is licensed under the same terms.
