# iosnoperiod

`iosnoperiod/` is an iOS-safe mirror of bundle files whose real repository paths contain leading periods.

Some iOS unzip, upload, file-picker, or inspection flows may hide, omit, or strip files and directories that begin with a period, such as `.github/`, `.stegverse/`, or `.gitkeep`.

Mapping rule:

```text
iosnoperiod/ = repository root
```

Examples:

```text
iosnoperiod/github/workflows/core-lite-intake.yml -> .github/workflows/core-lite-intake.yml
iosnoperiod/stegverse/ingest_manifest.json -> .stegverse/ingest_manifest.json
iosnoperiod/incoming/gitkeep -> incoming/.gitkeep
```

If a bundle appears to contain only `iosnoperiod.md` and `iosnoperiod/` on iOS, do not assume the bundle is invalid. The `iosnoperiod/` mirror is intentional.
