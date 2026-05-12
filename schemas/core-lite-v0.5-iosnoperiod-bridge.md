# Core-Lite v0.5: iosnoperiod Bridge

## Purpose

Core-Lite v0.5 adds an iOS-safe bridge for restoring leading-period files from `iosnoperiod/`.

## Bootstrap limitation

A GitHub Action cannot run from `iosnoperiod/github/workflows/...` because GitHub only recognizes workflows inside `.github/workflows/`.

For an empty repo, one seed workflow must still be created at:

```text
.github/workflows/install-iosnoperiod.yml
```

That seed can then restore all other leading-period paths from `iosnoperiod/`.

## Mapping

```text
iosnoperiod/github/workflows/core-lite-intake.yml -> .github/workflows/core-lite-intake.yml
iosnoperiod/stegverse/core-lite.json -> .stegverse/core-lite.json
iosnoperiod/incoming/gitkeep -> incoming/.gitkeep
```
