# Hermes Desktop Position and Surface Contracts

This reference captures the contribution positions verified by the Placement
Playground plugin. Treat each destination as its own SDK contract; do not assume
a component that renders in one area can be registered unchanged in another.

## Architecture: one plugin, surface-specific adapters

Keep shared logic separate from placement:

- shared state: current position, persistence, labels, previous/next/reset
- surface adapters: pane, status bar, title bar, popover, composer render,
  composer attachment provider, route, sidebar navigation
- permanent fallback controls: command-palette actions for Next, Previous,
  Reset, and Show Current Position

A position switch should dispose the active contribution, persist the new index,
then register exactly one adapter for the new surface. `when()` is not reactive;
a registry mutation is required when visibility or position changes.

## Position matrix

| Position | SDK area/contract | Payload |
|---|---|---|
| Pane · Main | `PANES_AREA` | `title`, `data: {placement: 'main'}`, `render()` |
| Pane · Left | `PANES_AREA` | `data: {placement: 'left', width}`, `render()` |
| Pane · Right | `PANES_AREA` | `data: {placement: 'right', width}`, `render()` |
| Pane · Top | `PANES_AREA` | `data: {placement: 'top', height}`, `render()` |
| Pane · Bottom | `PANES_AREA` | `data: {placement: 'bottom', height}`, `render()` |
| Dock · Workspace top | `PANES_AREA` | `data: {placement: 'top', dock: {pane: 'workspace', pos: 'top'}, height}` |
| Dock · Workspace bottom | `PANES_AREA` | `data: {placement: 'bottom', dock: {pane: 'workspace', pos: 'bottom'}, height}` |
| Dock · Workspace left | `PANES_AREA` | `data: {placement: 'left', dock: {pane: 'workspace', pos: 'left'}, width}` |
| Dock · Workspace right | `PANES_AREA` | `data: {placement: 'right', dock: {pane: 'workspace', pos: 'right'}, width}` |
| Dock · Workspace center | `PANES_AREA` | `data: {placement: 'main', dock: {pane: 'workspace', pos: 'center'}}` |
| Status bar · Left | `STATUSBAR_AREAS.left` | `render()` returning a compact ReactNode, or valid `StatusbarItem` data |
| Status bar · Right | `STATUSBAR_AREAS.right` | same contract as left |
| Title bar · Left | `TITLEBAR_AREAS.left` | `render()` returning a compact ReactNode |
| Title bar · Center | `TITLEBAR_AREAS.center` | `render()` returning a compact ReactNode |
| Title bar · Right | `TITLEBAR_AREAS.right` | `render()` returning a compact ReactNode |
| Popover · Top | render-slot anchor + `PopoverContent side='top'` | trigger ReactNode plus popover ReactNode |
| Popover · Bottom | render-slot anchor + `PopoverContent side='bottom'` | trigger ReactNode plus popover ReactNode |
| Popover · Left | render-slot anchor + `PopoverContent side='left'` | trigger ReactNode plus popover ReactNode |
| Popover · Right | render-slot anchor + `PopoverContent side='right'` | trigger ReactNode plus popover ReactNode |
| Composer · Top | `COMPOSER_AREAS.top` | `render()` |
| Composer · Bottom | `COMPOSER_AREAS.bottom` | `render()` |
| Composer · Leading | `COMPOSER_AREAS.leading` | `render()`; use a compact control |
| Composer · Actions | `COMPOSER_AREAS.actions` | `render()`; use a compact control |
| Composer · Attachments | `COMPOSER_AREAS.attachments` | `data: {label, icon, run}`; no `render()` |
| Workspace route + Sidebar | `ROUTES_AREA` + `SIDEBAR_NAV_AREA` | route uses `{path}` + `render()`; nav uses `{path, label, codicon}` |

The SDK also exposes `COMPOSER_AREAS.underside`, middleware, and microActions.
`underside` is a render seam; middleware and microActions are data-provider
contracts, not generic render positions.

## Exact title-bar distinction

`TITLEBAR_AREAS.left`, `.center`, and `.right` are generic render slots. Use:

```js
ctx.register({
  id: 'my-title-control',
  area: TITLEBAR_AREAS.left,
  render: () => jsx(Button, {
    size: 'icon-xs',
    variant: 'ghost',
    'aria-label': 'My title control',
    children: jsx(icons.LayoutDashboard, { size: 14 })
  })
})
```

Do not register a `TitlebarTool` object as `data` in those exported areas.
Declarative tool data is consumed by separate internal areas
`titleBar.tools.left/right`. Unless the SDK exports a public constant for them,
prefer the supported render-slot API.

Title/status render-slot icons are ReactNodes. By contrast, sidebar `codicon`
and `ComposerAttachmentProvider.icon` are codicon-name strings.

## Status-bar contract

A custom stateful status widget can own its slot with top-level `render()`.
For data contributions, `StatusbarItem.label`, `detail`, `icon`, and
`menuContent` are ReactNodes. `StatusbarMenuItem.label` is a string while its
`icon` is a ReactNode. Keep status controls compact and provide an accessible
name or tooltip.

## Popover positioning and collision avoidance

A popover side is relative to its trigger. Do not test top/bottom from a trigger
at the bottom status bar: Radix collision avoidance will flip `side='bottom'`
upward when there is no room, making top and bottom appear identical.

Use an anchor with space on all four sides. A verified test pattern mounts a
fixed, viewport-centered trigger through an untransformed title-bar slot:

```js
ctx.register({
  id: 'popover-anchor',
  area: TITLEBAR_AREAS.left,
  render: () => jsx(Popover, {
    defaultOpen: true,
    children: [
      jsx(PopoverTrigger, {
        asChild: true,
        children: jsx('button', {
          className: 'fixed left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2'
        })
      }),
      jsx(PopoverContent, {
        side: 'top',
        align: 'center',
        sideOffset: 8,
        children: jsx(MyContent, {})
      })
    ]
  })
})
```

Do not mount that fixed trigger through `TITLEBAR_AREAS.center`: the center slot
itself uses CSS transforms, which creates a containing block for fixed
descendants and can pin the trigger near the title bar instead of the viewport
center.

Keep collision avoidance enabled for production UI. Disabling it only to force a
side can place content off-screen.

## Composer contracts

These are render seams:

- `COMPOSER_AREAS.top`
- `COMPOSER_AREAS.bottom`
- `COMPOSER_AREAS.underside`
- `COMPOSER_AREAS.leading`
- `COMPOSER_AREAS.actions`

`leading` and `actions` have little space; adapt the shared UI to a small button
or icon instead of rendering a full card.

Attachments are declarative providers:

```js
ctx.register({
  id: 'my-attachment-provider',
  area: COMPOSER_AREAS.attachments,
  data: {
    label: 'My provider',
    icon: 'layout',
    run: composer => composer.insertText('[My provider]')
  }
})
```

The provider appears only inside the composer's `+` attachment menu. It is not
supposed to remain visible inline. Verify it by opening the menu, selecting the
row, and confirming `run()` changes the composer as expected.

Because data-only positions cannot render Previous/Next controls, keep command
palette navigation available globally.

## Route and sidebar contract

Register the route and nav row together and dispose them together:

```js
const disposeRoute = ctx.register({
  id: 'page',
  area: ROUTES_AREA,
  data: { path: '/my-page' },
  render: () => jsx(MyPage, {})
})
const disposeNav = ctx.register({
  id: 'nav',
  area: SIDEBAR_NAV_AREA,
  data: { path: '/my-page', label: 'My Page', codicon: 'layout' }
})
```

Use `host.navigate('/my-page')` when entering the route position. `path`,
`label`, and `codicon` are strings; route contents come from `render()`.

## Verification checklist

- Run `node --check plugin.js` for syntax.
- Confirm hot reload produces no plugin failure toast.
- Inspect the actual destination in the Desktop UI; do not infer success only
  from registration.
- For pane positions, verify the correct zone and tab title.
- For title/status slots, verify the element appears in the accessibility tree
  with the expected label.
- For popovers, compare each side around the same centered anchor.
- For composer attachments, open the `+` menu and execute the provider.
- For routes, navigate to the route and verify its sidebar row is active.
- Hot-reload once more and verify `ctx.storage` restores the current position.
- Avoid automation double-clicks on self-disposing controls: a synthetic click
  can deliver more than one event while the clicked contribution unregisters.
  Prefer command-palette navigation or an explicit one-time test position when
  verifying a disappearing control.
