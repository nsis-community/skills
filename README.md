# Agent skills for NSIS

![License](https://img.shields.io/github/license/nsis-community/skills?color=blue&style=for-the-badge)

[Agent skills](https://agentskills.io) for working on NSIS packages with Claude Code, Codex and other coding agents.

| Skill                                                      | What it does                                                                                                                                                                                                                                                                                                                       |
| ---------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| [nsis-package-layout](skills/nsis-package-layout/SKILL.md) | Turns a plug-in, header or other contrib download (zip, installer, loose files) into a repository that follows the [NSIS Package Layout Specification](https://github.com/nsis-dev/release-package/blob/main/SPEC.md), with README, `.gitattributes` and a [release-package](https://github.com/nsis-dev/release-package) workflow |

## Installation

```bash
npx skills add nsis-community/skills
```

Or copy or symlink a folder under `skills/` into your agent's skills directory, such as `~/.claude/skills/`.

The skills call `python3`, `git` and [7-Zip](https://www.7-zip.org/) (`7zz`).

## License

See [LICENSE](LICENSE).
