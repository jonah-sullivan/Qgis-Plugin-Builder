# Security Policy

## Supported Versions

Security fixes are released for the latest version of each supported plugin.
Update through the QGIS Plugin Manager to receive them.

| Plugin           | QGIS version | Branch    | Supported      |
| ---------------- | ------------ | --------- | -------------- |
| Plugin Builder 4 | 4.x          | `QGIS4`   | Latest release |
| Plugin Builder 3 | 3.x          | `QGIS3`   | Latest release |
| Plugin Builder 2 | 2.x          | `LTR_2.x` | No             |

## Reporting a Vulnerability

**Please do not report security vulnerabilities through public GitHub issues,
pull requests, or discussions.**

Report them privately using GitHub's
[private vulnerability reporting](https://github.com/jonah-sullivan/Qgis-Plugin-Builder/security/advisories/new)
(the **Report a vulnerability** button on the repository's **Security** tab).

Please include:

- Which plugin and version is affected (Plugin Builder 3 or 4)
- A description of the issue and its impact
- Steps to reproduce, or a proof of concept
- Any suggested fix, if you have one

Reports will be handled as soon as possible. You will be kept informed while
the issue is investigated and fixed, and credited in the published advisory
unless you prefer to remain anonymous.

## Scope

In scope:

- The Plugin Builder plugins themselves
- The code templates Plugin Builder generates. A vulnerability that every
  generated plugin would inherit is especially important to report
- This repository's build, release and CI workflows

Out of scope:

- Vulnerabilities in QGIS itself. Report these to the
  [QGIS project](https://github.com/qgis/QGIS/security)
- Vulnerabilities in plugins that were generated with Plugin Builder and then
  modified, unless the issue comes from the unmodified template
- Vulnerabilities in third-party dependencies, which should be reported
  upstream (a heads-up here is still welcome if Plugin Builder is affected)
