# iosnoperiod

## Purpose

`iosnoperiod/` is an iOS-safe mirror of bundle files whose real repository paths contain leading periods.

Some iOS unzip, upload, file-picker, or inspection flows may hide, omit, or strip files and directories that begin with a period, such as:

```text
.github/
.stegverse/
.gitkeep
```

This can make a valid StegVerse bundle look incomplete when viewed on iOS.

In the worst case, an iOS user may uncompress or inspect a bundle and see only:

```text
iosnoperiod.md
iosnoperiod/
```

That does not mean the bundle is empty or broken. It usually means iOS is hiding or stripping the leading-period paths.

## Mapping Rule

```text
iosnoperiod/ = repository root
```

Files inside `iosnoperiod/` mirror their intended repository locations, but without leading periods anywhere in the file path.

## Examples

```text
iosnoperiod/github/workflows/core-lite-intake.yml
  -> .github/workflows/core-lite-intake.yml

iosnoperiod/github/workflows/install-iosnoperiod.yml
  -> .github/workflows/install-iosnoperiod.yml

iosnoperiod/stegverse/core-lite.json
  -> .stegverse/core-lite.json

iosnoperiod/stegverse/ingest_manifest.json
  -> .stegverse/ingest_manifest.json

iosnoperiod/incoming/gitkeep
  -> incoming/.gitkeep
```

## Why This Exists

StegVerse bundles often require files that GitHub recognizes only when they use leading-period paths.

For example:

```text
.github/workflows/
```

is required for GitHub Actions workflows.

```text
.stegverse/
```

is used for StegVerse manifests, policies, receipts, registries, and core-lite metadata.

```text
.gitkeep
```

is used to preserve otherwise-empty directories such as `incoming/`.

If iOS hides or strips these paths, a user may not see the files needed for installation, workflow recognition, or ingestion. The `iosnoperiod/` mirror preserves a visible copy of those files.

## Manual Use

When installing manually from iOS:

```text
1. Open iosnoperiod/.
2. Treat iosnoperiod/ as the repository root.
3. Copy each file to the matching repository path.
4. Restore the leading periods shown in the examples above.
```

Example:

```text
Copy:
  iosnoperiod/github/workflows/core-lite-intake.yml

To:
  .github/workflows/core-lite-intake.yml
```

## Core-Lite Use

Core-Lite may restore these files automatically where a restore workflow or ingestion engine is already available.

The restore rule is:

```text
iosnoperiod/github/     -> .github/
iosnoperiod/stegverse/  -> .stegverse/
iosnoperiod/incoming/gitkeep -> incoming/.gitkeep
```

## Important Limitation

GitHub cannot run a workflow from:

```text
iosnoperiod/github/workflows/
```

GitHub Actions only recognizes workflows from:

```text
.github/workflows/
```

Therefore, for an empty repo, one seed workflow may still need to be created manually at:

```text
.github/workflows/install-iosnoperiod.yml
```

After that seed workflow exists, it can restore the remaining leading-period files from `iosnoperiod/`.

## Integrity Note

If a bundle appears to contain only `iosnoperiod.md` and `iosnoperiod/` on iOS, do not assume the bundle is invalid.

Check whether the hidden leading-period paths are present through another tool, or restore them from the `iosnoperiod/` mirror.

The presence of `iosnoperiod/` is intentional. It is a compatibility layer for iOS users, not a replacement for the real repository paths.
