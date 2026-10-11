"""Web development: Node and the usual VS Code companions."""

from rigsmith.library._util import ext, tool

tool("node", "Node.js and npm.")
tool("pnpm", "Fast, disk-efficient Node package manager.")
tool("bun", "All-in-one JS runtime, bundler, test runner and package manager.")
tool("deno", "Secure TypeScript/JavaScript runtime with batteries included.")
tool("biome", "Fast formatter and linter for JS/TS/JSON/CSS (Prettier + ESLint in one).")
ext("eslint-ext", "dbaeumer.vscode-eslint", "ESLint in VS Code.")
ext("prettier-ext", "esbenp.prettier-vscode", "Prettier formatter for JS/TS/CSS/HTML/Markdown.")
ext("biome-ext", "biomejs.biome", "Biome formatter and linter in VS Code.")
ext("deno-ext", "denoland.vscode-deno", "Deno language support in VS Code.")
ext("tailwind-ext", "bradlc.vscode-tailwindcss", "Tailwind CSS class completion and previews.")
ext("vue-ext", "Vue.volar", "Vue 3 language support (Volar).")
ext("svelte-ext", "svelte.svelte-vscode", "Svelte language support.")
ext("auto-rename-tag", "formulahendry.auto-rename-tag", "Rename the paired HTML/XML tag automatically.")
ext("color-highlight", "naumovs.color-highlight", "Highlight CSS colors in their own color.")
ext("react-snippets", "dsznajder.es7-react-js-snippets", "React/Redux/JS snippets (rafce, useState…).")
ext("rest-client", "humao.rest-client", "Send HTTP requests from .http files, Postman-style, inside VS Code.")
