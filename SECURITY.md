# Security

rigsmith installs software and edits shell and editor configuration, sometimes with `sudo`, so security
reports are taken seriously.

## Reporting a vulnerability

**Please don't open a public issue.** Report it privately through
[GitHub's private vulnerability reporting](https://github.com/slimfrkha/rigsmith/security/advisories/new).
Include what you found, how to reproduce it, and what an attacker could do with it.

You'll get an acknowledgement within a week. Fixes ship as a new patch release, with an advisory once
users can upgrade.

## Supported versions

Only the latest release gets security fixes.

## Scope

In scope: anything rigsmith itself does: how it runs commands, writes files, edits `~/.zshrc` and
settings, handles `sudo`, and what `install.sh` downloads and runs.

Out of scope: vulnerabilities in the tools rigsmith installs (report those upstream), and things a
user's own config or `~/.config/rigsmith/artifacts/*.py` plugins do (plugins are code you choose to run).
