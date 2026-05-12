# iosnoperiod Directory

This directory exists to preserve files and paths that normally begin with a leading period.

Some iOS upload, unzip, file-picker, or archive workflows may hide, omit, rename, or strip leading-period files and directories such as `.github`, `.stegverse`, or `.gitkeep`.

The `iosnoperiod/` directory mirrors the intended repository root structure without using any leading-period path segments.

Mapping rule:

```text
iosnoperiod/ = repository root
```

Examples:

```text
iosnoperiod/github/workflows/core-lite-intake.yml
  -> .github/workflows/core-lite-intake.yml

iosnoperiod/stegverse/ingest_manifest.json
  -> .stegverse/ingest_manifest.json

iosnoperiod/incoming/gitkeep
  -> incoming/.gitkeep
```

When installing manually from iOS, copy files from `iosnoperiod/` into the repository root and restore the leading-period path names shown in the mapping or ingest manifest.
