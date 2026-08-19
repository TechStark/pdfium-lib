# WASM package API

The npm package published from this repository exposes the generated PDFium WebAssembly bindings through a thin wrapper.

## Installation

```bash
npm install @techstark/pdfium
```

## Entry points

The package exposes two helper entry points:

- `loadPdfium(moduleOverrides?)`
- `createPdfiumModule(moduleOverrides?)`

Both functions are aliases and return the underlying Emscripten module factory result.

### CommonJS

```js
const { loadPdfium } = require('@techstark/pdfium');

async function main() {
  const pdfium = await loadPdfium();
  console.log(typeof pdfium.ccall, typeof pdfium.cwrap);
}

main().catch(console.error);
```

### ES modules

```js
import { loadPdfium } from '@techstark/pdfium';

const pdfium = await loadPdfium();
console.log(typeof pdfium.ccall, typeof pdfium.cwrap);
```

## Notes

- This package ships the generated Emscripten artifacts directly (`pdfium.js`, `pdfium.wasm`, `pdfium.esm.js`, `pdfium.esm.wasm`).
- It is intended for low-level integrations that want to call the underlying PDFium bindings explicitly.
- The package is not a high-level PDF SDK.
- The module is still subject to the same Emscripten/PDFium runtime constraints as the generated bindings themselves.

## Related docs

- [docs/PUBLISH_NPM.md](PUBLISH_NPM.md)
- [README.md](../README.md)
