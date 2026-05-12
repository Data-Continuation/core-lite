# Core-Lite Empty Repo Install v0.9.0

## Purpose

Install a complete Core-Lite engine into an empty or newly created Org-level core-lite repository.

## Done criteria

```text
1. core_lite/ source files exist.
2. schemas/ policy and validation files exist.
3. incoming/.gitkeep exists.
4. .stegverse/core-lite.json exists.
5. .github/workflows/core-lite-intake.yml exists.
6. iosnoperiod/ mirrors all leading-period paths.
7. Future upgrades can be uploaded to incoming/*.zip.
```

## Manual empty-repo bootstrap note

GitHub cannot run a workflow until a workflow exists under:

```text
.github/workflows/
```

If iOS strips or hides leading-period paths, use:

```text
iosnoperiod/github/workflows/core-lite-intake.yml
```

as the visible source and create the real workflow at:

```text
.github/workflows/core-lite-intake.yml
```

After this install, use:

```text
incoming/<bundle>.zip
```

for future Core-Lite upgrades.
