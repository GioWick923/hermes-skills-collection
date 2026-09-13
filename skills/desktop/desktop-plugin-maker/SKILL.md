---
name: desktop-plugin-maker
description: Build, verify, and package Hermes Desktop plugins.
version: 1.0.0
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [desktop, plugins, ui, extension]
    category: productivity
    related_skills: []
---

# Desktop Plugin Maker

Write plugins for the Hermes desktop app: statusbar items, layout panes,
command-palette commands, keybinds, routes, and themes. A plugin is a single
plain-JavaScript ESM file the app loads at runtime — no build step, no repo
changes. A plugin can also talk to its own Python backend namespace
(`ctx.rest`/`ctx.socket` → `/api/plugins/<id>`); the general Python plugin
system (`~/.hermes/plugins/`) is otherwise documented separately.

Full human reference (every export, area payloads, backend, security):
`website/docs/developer-guide/desktop-plugin-sdk.md`.

Verified placement contracts and the complete 25-position test matrix:
`references/position-surface-contracts.md`. Load this reference whenever a
plugin must move across panes, docks, bars, popovers, composer seams, routes,
or sidebar navigation.

**Placement invariant:** keep one shared logical state but implement a separate
adapter for each destination contract. Render slots use `render() => ReactNode`;
data-provider areas use their exact declarative payload. Never move the same
unadapted contribution object across unlike areas.

## When to Use

- The user asks for a new desktop UI element (a pane, a statusbar widget, a
  dashboard, a command) without modifying the app itself.
- You want to surface data you compute (via gateway RPC) inside the app.

## Prerequisites

- The Hermes desktop app (it loads plugins; the CLI/gateway alone does not).
- Write access to `$HERMES_HOME/desktop-plugins/` (usually
  `~/.hermes/desktop-plugins/`).

## How to Run

1. Create `$HERMES_HOME/desktop-plugins/<name>/plugin.js` from
   `templates/plugin.js` (relative to this skill directory) — that's
   `~/.hermes/...` by default, or `~/.hermes/profiles/<profile>/...` under a
   named profile. Keep `<name>` equal to the plugin `id`.
2. The desktop app watches that directory: the plugin loads within a few
   seconds of the file landing, and every later save hot-reloads it in
   place. No reload step. (Fallback if it doesn't appear: ⌘K →
   **Reload desktop plugins**.)
3. If loading fails the app shows a toast naming the error — fix the file
   and save again.

## Quick Reference

The ONLY import surface is `@hermes/plugin-sdk` (plus `react` /
`react/jsx-runtime`, which resolve to the app's own React — write UI with
`jsx()` calls, not JSX syntax; the file is not compiled).

- `host.state.*` — readonly reactive atoms: `activeSessionId`, `cwd`,
  `gateway`, `model`, `profile`, `viewport`. Read with `.get()` in handlers,
  `useValue(atom)` in components.
- `host.request(method, params)` — gateway JSON-RPC (sessions, config,
  skills, cron — everything the app uses).
- `host.onEvent(type, fn)` — live gateway events (`'*'` for all). Returns a
  disposer.
- `host.notify({ kind, message })`, `host.navigate(path)`, `host.logs(...)`,
  `host.status()`, `haptic('tap')`.
- `ctx.register({ id, area, order?, render?, data? })` — contribute UI.
  Key areas: `'statusBar.right'`/`'statusBar.left'` (chips),
  `'panes'` (layout zones — set `title` and
  `data: { placement, dock?, width?, height? }`; the pane auto-joins a
  matching zone), `PALETTE_AREA` (⌘K commands), `KEYBINDS_AREA` (rebindable
  actions).
- Pane placement: `placement: 'left'|'right'|'bottom'|'main'` is the
  semantic role — the pane stacks (tabs) with existing panes of that role.
  To land on a specific EDGE instead, add `dock: { pane, pos }` — the same
  gesture as dragging onto a pane's drop chip. `pane` is any pane id
  (`workspace` is the main thread; also `sessions`, `terminal`, `files`,
  `review`, `logs`), `pos` is `'top'|'bottom'|'left'|'right'|'center'`.
  E.g. "below the conversation" = `dock: { pane: 'workspace', pos: 'bottom' }`
  — declare a `height` (e.g. `'200px'`) so it doesn't take half the zone.
- Full PAGES: register `area: ROUTES_AREA` with `data: { path: '/my-page' }`
  and a `render` — the page mounts in the workspace (main) pane like any
  built-in view. Make it reachable with a sidebar nav row:
  `ctx.register({ id: 'nav', area: SIDEBAR_NAV_AREA, data: { path: '/my-page', label: 'My Page', codicon: 'project' } })`
  (renders below Artifacts, lights up at the route) — and/or a
  `PALETTE_AREA` command calling `host.navigate('/my-page')`.
- `ctx.storage.get/set/remove` — persistence namespaced to your plugin.
- `ctx.i18n.register({ en, ja, ... })` — ship your OWN locale bundles, scoped
  to your plugin (never edit core `en.ts`). Values are literal strings or
  interpolator functions; nested trees are addressed by dot-path. Read them
  reactively in components with `usePluginI18n(id)` returning `t('key', ...args)`
  (re-renders on a locale switch), or via `ctx.i18n.t` in handlers/stores.
  Resolution follows the app's active locale, then your `en`, then the raw key.
- Data: `useQuery`/`useMutation`/`useQueryClient`/`queryClient` (the app's ONE
  React Query client — cache, dedupe, `refetchInterval`, invalidate like core;
  never hand-roll a poll loop), plus `atom`/`computed` for plugin-local state.
- Backend: if the plugin ships a Python `plugin_api.py` (under
  `~/.hermes/plugins/<id>/dashboard/`, manifest `"api": "plugin_api.py"`), reach
  it with `ctx.rest('/path', { method?, body?, timeoutMs? })` and its live twin
  `ctx.socket('/events', onMessage)` — both scoped to `/api/plugins/<id>` by
  construction (traversal rejected). `ctx.socket` is a **no-op on OAuth
  remotes**, so always keep a polling fallback. The Python backend is imported
  only when the plugin is in `plugins.enabled` in `config.yaml` (separate from
  the in-app enable toggle). For gateway-wide data use `host.request` /
  `host.onEvent` instead.

  For a local backend-only desktop plugin, `hermes plugins enable <id>` may say
  the plugin is not installed when only `dashboard/manifest.json` exists. Add a
  minimal root `plugin.yaml` plus an empty `__init__.py`, then run the enable
  command again. This writes `plugins.enabled` as a real YAML list. Do not use
  `hermes config set plugins.enabled '["<id>"]'`: some versions serialize that
  as a quoted scalar, so the API will not mount. Restart the Desktop gateway
  after enabling because Python routes mount only at startup.
- `Contribute` (mount-scoped): render `jsx(Contribute, { area, id, children })`
  inside a component so page-owned chrome (e.g. a titlebar control in
  `TITLEBAR_AREAS.center`) leaves when the page unmounts — `ctx.register` is for
  permanent contributions.
- `defaultEnabled: false` on the default export ships an opt-in plugin: it
  inventories in Settings → Plugins, off until the user flips it on.
- Users manage plugins in Settings → Plugins (enable/disable live, reveal
  folder). A disabled plugin stays disabled across restarts — don't fight
  it; the user turned you off.
- UI: the app's design language, importable directly — `Button`, `Input`,
  `Textarea`, `Select*`, `Switch`, `Checkbox`, `SegmentedControl`, `Tabs*`,
  `Dialog*`, `ConfirmDialog`, `DropdownMenu*`, `ContextMenu*`, `Popover*`,
  `Tip`/`Tooltip*`, `Badge`, `Kbd`/`KbdGroup`, `SearchField`, `ScrollArea`,
  `Separator`, `Skeleton`, `GlyphSpinner`, `EmptyState`, `ErrorState`,
  `CopyButton`, `StatusDot`, `LogView`, `Codicon`, `DecodeText`, plus `cn`
  and `icons.*`. Prefer these over hand-rolled elements so the plugin looks
  native; style with theme vars, never hardcoded colors.

## Procedure

1. Pick a short kebab-case `id`; the folder name must match.
2. Start from `templates/plugin.js`; keep the default export shape
   (`{ id, name, register(ctx) }`).
3. For a pane, register `area: 'panes'` with a `placement` hint and a
   `render` returning your component — the app places it into a sensible
   zone automatically; the user can drag it anywhere afterwards.
4. Fetch data with `host.request` and/or subscribe with `host.onEvent`;
   never poll faster than a few seconds.
5. Write the file with your file tools, then ask the user to run
   **Reload desktop plugins** from ⌘K.

## Production Packaging and Migration

### Open-source repository layout

When publishing examples, keep each desktop plugin self-contained under
`plugins/<id>/plugin.js`. If it requires a backend, include only the portable
backend package (`plugin.yaml`, `__init__.py`, `dashboard/manifest.json`, and
`dashboard/plugin_api.py`) in the matching `plugins/<id>/` folder. Document the
separate install locations clearly:

```text
repo/plugins/<id>/plugin.js             → <HERMES_HOME>/desktop-plugins/<id>/plugin.js
repo/plugins/<id>/dashboard/...         → <HERMES_HOME>/plugins/<id>/dashboard/...
```

Ship a root README, per-plugin README where setup differs, a license, and a
`.gitignore`. Exclude credentials, OAuth artifacts, account/device/wallet data,
state databases, logs, local paths, ROMs/media/save files, and `node_modules`.
Never substitute a demo artifact (for example, an HTML deck) for the requested
plugin source: keep a presenter/launcher generic unless the user specifically
asks to bundle a particular artifact.

Before publishing, scan the export for usernames, home paths, key/token
patterns, bearer headers, and accidental binary/user-data files. Also check that
README links point to actual current folders.

### Rename invariant

The disk-plugin folder, exported `id`, backend namespace, storage namespace,
and palette command IDs normally share one kebab-case identifier. A rename must
update all of them together, then remove the obsolete folder:

1. Change the exported plugin `id` and command/storage identifiers.
2. Rename both desktop and backend directories if a backend exists.
3. Update README links and installation paths.
4. Verify the old folder is absent and the new `plugin.js` parses.

A visible product name may remain more descriptive than its stable ID (for
example, `id: 'markets'`, name: `Hyperliquid Markets`).

### Embedded documents and local files

For a route that presents a user-selected local HTML document, use the browser
File API (`await file.text()`) and assign the result to an iframe `srcdoc`.
This keeps the content in memory: do not upload, copy, index, or persist it
unless the user explicitly requests a storage design.

Treat chosen HTML as active content. Embed it in a sandboxed iframe with the
minimum permissions required; never give it Hermes APIs, plugin storage, or
filesystem access. State the supported format and unsupported conversions
clearly—an HTML presenter is not automatically a PowerPoint/PDF renderer.

Routes unmount when users navigate away. If preserving a live iframe/emulator
session is required, create it once at module scope, move it into a hidden
parking container on unmount, and reattach it on return. This preserves only
in-memory state until Hermes closes or the plugin reloads; use the underlying
app's own save mechanism for durable state. Do not simulate persistence by
copying private user files into plugin storage.

## Verification

1. Run `node --check plugin.js` **from the plugin directory**. On this
   On Windows/MSYS, absolute Windows paths can be translated incorrectly by
   automatic linting.
2. For a Python bridge, run `python -m py_compile dashboard/plugin_api.py`;
   parse JSON manifests explicitly.
3. Do a focused ad-hoc static contract check when a plugin is added, renamed,
   or converted (IDs/folders, expected contribution areas, no unsupported
   imports, and no stale links). This is verification evidence, not a claim
   that a full test suite passed.
4. For an export, inventory the expected plugin folders, assert obsolete paths
   are absent, and run the privacy scan described above.
5. Only with the user's explicit permission, use `computer_use` to visually
   confirm a hot-loaded plugin's route/surface and its key interaction.

## Pitfalls

- **Title-bar areas have two distinct contracts.** `TITLEBAR_AREAS.left`, `.center`, and `.right` are generic render slots: register them with `render: () => ReactNode`, or mount `<Contribute area={TITLEBAR_AREAS.*}>...</Contribute>`. Do not put a `TitlebarTool` object in `data` for these exported areas. The shell consumes declarative tool data from separate internal areas (`titleBar.tools.left/right`); unless the SDK exposes a public constant for those, use the supported render-slot API.
- Icon types are surface-specific: title/status render slots use ReactNodes; sidebar `codicon` and `ComposerAttachmentProvider.icon` use codicon-name strings.
- `COMPOSER_AREAS.attachments` is a data-provider area, not a render slot. Register `{data: {label, icon, run}}`; use `render()` only for composer `top`, `bottom`, `underside`, `leading`, and `actions`.


- NEVER hardcode colors or backgrounds (`#000`, `black`, `rgb(...)`). Panes
  already sit on the app's editor background — leave the background alone
  and use theme variables for everything else: `var(--ui-text-secondary)`,
  `var(--ui-text-quaternary)`, `var(--ui-stroke-secondary)`,
  `var(--ui-accent)`. For canvas drawing, resolve them once with
  `getComputedStyle(canvas).getPropertyValue('--ui-accent')`.
- Reference only what you imported — a component you forgot to import
  (e.g. `StatusDot`) is a ReferenceError at render. Double-check every
  identifier in your `jsx()` calls appears in the import line.
- Canvas panes MUST track their container with a `ResizeObserver` and
  re-size the canvas (width/height attributes, not just CSS) — panes resize
  constantly (sash drags, layout switches); a mount-time-only size leaves
  blank space or blurry scaling.
- JSX syntax will not parse — the file loads uncompiled. Use
  `jsx('div', { children: ... })` from `react/jsx-runtime`.
- On this Windows/MSYS host, automatic `write_file` Node lint can mis-translate an absolute `C:\\...` path to `C:\\c\\...` and report a false `MODULE_NOT_FOUND`. Verify with `node --check plugin.js` from the plugin folder.
- Do not import anything except `@hermes/plugin-sdk`, `react`, and
  `react/jsx-runtime`; other specifiers fail to resolve.
- Handlers must read state imperatively (`$atom.get()`), never from render
  closures — rapid events will otherwise see stale values.
- Keep components small; subscribe (`useValue`) only in the leaf that
  renders the value.

### Visual checks

- The plugin's UI appears after **Reload desktop plugins**.
- No error toast ("Plugin <name> failed to load") appears; if it does, the
  message names the failure — fix and reload.
- For panes: the new zone is visible and draggable like any core pane.
