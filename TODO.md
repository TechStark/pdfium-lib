# npm package publishing improvement plan

## Status

- [x] Add automatic npm versioning based on workflow run metadata
- [x] Improve package README with install and usage examples
- [x] Add a fresh-install smoke test for the published package
- [x] Reduce GitHub Actions runtime for the wasm workflow
- [x] Resolve the apt-cache save warning by narrowing the cache scope to actual `.deb` archives
- [x] Add a minimal wrapper API for easier consumption
- [x] Switch initial publish to a prerelease/dist-tag flow (for example `beta`)
- [x] Add release notes / publish documentation
- [x] Add richer TypeScript declarations for the npm package entry points
- [x] Add package API documentation for consumers

## Completed work

- Added `loadPdfium` and `createPdfiumModule` wrappers in the generated npm package entry points.
- Updated the generated TypeScript declarations to describe the wrapper API and common module surface.
- Added package-focused usage docs in [docs/WASM_PACKAGE_API.md](docs/WASM_PACKAGE_API.md).
- Updated the workflow publishing flow to validate the package locally and publish under the `beta` dist-tag.

## Notes

- The package still ships raw Emscripten/PDFium bindings rather than a high-level PDF SDK.
- For future follow-ups, the next natural step would be integrating the wrapper into downstream consumers or expanding the package API surface further.
