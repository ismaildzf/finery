# Contributing

Thanks for helping. Small, focused pull requests are easiest to review.

## Build

The project targets seven Minecraft versions with [Stonecutter](https://stonecutter.kikugie.dev/).

```bash
./gradlew "Set active project to 1.21.1" --console=plain -q
./gradlew :1.21.1:build
```

Always run the `Set active project` task before building — Stonecutter rewrites the source tree for the selected version, and building a version without selecting it first compiles the wrong branch.

## Code rules

- Version-specific code lives inside Stonecutter markers (`//? if <1.21 { ... } else { ... }`). Keep shared logic outside them.
- Client-side rendering: a cosmetic renders through one of the baked renderers (`BakedHeadModel`, `BakedNeckModel`) or the custom mesh builders. Do not add per-version renderer copies.
- Never commit `run/`, build output, tokens or personal skins.

## Pull requests

1. Describe the change and the piece it affects.
2. Say which versions you built.
3. Attach a screenshot for anything visual.

## Issues

Use the issue templates. Reports without a mod version and a log may be closed as incomplete.
