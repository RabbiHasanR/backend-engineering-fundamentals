# Ember project template

A reusable template for starting a production-grade, scalable Ember web app:
official blueprint + WarpDrive (EmberData) data layer with request builders and
handlers + Tailwind CSS v4 + test-first setup (QUnit, MSW, Playwright).

**How to use this file**

- By hand: follow section 1, then create the files in sections 4 and 5.
- With Claude Code: put this file in the repo (for example `specs/web-template.md`)
  and ask it to scaffold the web app from it, one section at a time.

**Placeholders**

| Placeholder | Replace with |
|---|---|
| `<app-name>` | the project's package name, e.g. `colivo-web` |
| `__APP__` | the same name, inside test imports (`__APP__/data/...`) |
| `VITE_API_HOST` | the backend URL per environment |

**Decisions baked in**

- Ember: latest stable 7.x for a new app; pin to the newest LTS once it is promoted.
- TypeScript, `.gts` components, Glint, pnpm, Vite build (blueprint defaults).
- Data: Model classes + `store.request` with **builders and handlers**. No
  adapters or serializers; they are the legacy path.
- CSS: Tailwind CSS v4 through its Vite plugin; design tokens in `@theme`;
  utility classes wrapped in `components/ui/`.
- Backend contract: REST with an envelope `{ success, message, data, meta? }`.
- Tests: test-first; MSW mocks only the HTTP boundary; end-to-end uses the real backend.

---

## 1. Create the project

```bash
# 1. Generate with the official blueprint (build config always comes from it)
npx ember-cli@latest new <app-name> --typescript --pnpm
cd <app-name>

# 2. Test and tooling dependencies
pnpm add -D msw @playwright/test openapi-typescript eslint-plugin-boundaries
pnpm exec msw init public --save
pnpm exec playwright install chromium

# 3. Tailwind CSS v4 (then follow section 4 to enable the Vite plugin)
pnpm add -D tailwindcss @tailwindcss/vite prettier-plugin-tailwindcss

# 4. Folders the blueprint does not create
mkdir -p app/data/{handlers,builders,types} app/models app/utils \
         app/components/{ui,layout} \
         tests/{helpers,acceptance,integration/components/ui,unit/data} e2e docs
```

Optional addons, added when needed: `ember-intl` (translations, currency,
dates), `ember-concurrency` (async tasks, double-submit protection),
`ember-simple-auth` (refresh tokens, multiple authenticators).

---

## 2. Architecture

### Directory structure

```
app/
├── data/                     # the whole data layer; nothing else talks HTTP
│   ├── config.ts             # API host and namespace
│   ├── handlers/
│   │   ├── errors.ts         # network errors -> ApiError (403/404/422/...)
│   │   ├── auth.ts           # bearer token, 401 reporting
│   │   └── api-envelope.ts   # response envelope -> JSON:API (the "serializer")
│   ├── builders/             # one file per resource (the "adapter")
│   ├── lifetimes.ts          # cache policy
│   └── types/                # api.generated.ts from the backend's openapi.json
├── models/                   # Model classes (@attr, @belongsTo, @hasMany)
├── services/                 # store, session, app-wide state
├── routes/                   # thin: call store.request, guard access
│   └── authenticated/        # everything behind login
├── templates/                # thin: compose components
├── components/
│   ├── ui/                   # domain-free design system (button, modal, field)
│   ├── layout/               # page shell, navbar, sidebar
│   └── <feature>/            # one folder per feature
├── helpers/  modifiers/
├── utils/                    # pure functions, no Ember imports
└── styles/                   # app.css: Tailwind import, @theme tokens, base styles
tests/
├── unit/{utils,services,data}/
├── integration/components/
├── acceptance/
└── helpers/                  # msw.ts, login.ts, factories
e2e/                          # Playwright, real backend
```

### Rules

1. **Dependencies point one way:** `routes -> components -> services -> data -> utils`.
   `components/ui` never imports a feature folder. Components never import
   `data/handlers`.
2. **Thin edges.** Routes load data and guard access. Templates compose
   components. Rules and calculations live in `utils/` and services.
3. **One place knows the API shape.** Only `data/handlers/api-envelope.ts`
   understands the response envelope. Only `data/` calls the network.
4. **Data down, actions up.** Components receive data as args and call
   functions passed to them. Shared state lives in services with `@tracked`.
5. **A new feature touches a predictable set:** one model, one builder file,
   one route folder, one component folder, and their tests. If a shared file
   has to change, question the design.
6. **Select by `data-test-*`** in tests, never by CSS class.
7. **Extract only when it hurts.** When `components/ui` or `data/` gets large,
   move it to a pnpm workspace package. These boundaries make that mechanical.

### Adding a resource

1. `app/models/meal.ts` with the Model class.
2. `app/data/builders/meals.ts`: `export const meals = resourceBuilders('meal', 'meals');`
3. In a route: `const { content } = await this.store.request(meals.list({ month }));`
4. After a mutation, refetch or invalidate the lists it affects.

### Enforcing rule 1

Add `eslint-plugin-boundaries` and declare the layers in the generated ESLint
config:

```js
settings: {
  'boundaries/elements': [
    { type: 'utils', pattern: 'app/utils/*' },
    { type: 'data', pattern: 'app/data/*' },
    { type: 'services', pattern: 'app/services/*' },
    { type: 'ui', pattern: 'app/components/ui/*' },
    { type: 'components', pattern: 'app/components/*' },
    { type: 'routes', pattern: 'app/{routes,templates}/*' },
  ],
},
rules: {
  'boundaries/element-types': ['error', {
    default: 'disallow',
    rules: [
      { from: 'data', allow: ['utils'] },
      { from: 'services', allow: ['data', 'utils'] },
      { from: 'ui', allow: ['utils'] },
      { from: 'components', allow: ['ui', 'services', 'utils'] },
      { from: 'routes', allow: ['components', 'ui', 'services', 'data', 'utils'] },
    ],
  }],
},
```

---

## 3. Testing (TDD)

Same process as the backend: test first, see it fail, minimum code, refactor on
green, one behaviour at a time.

### Project settings

| Setting | Value |
|---|---|
| System type | Web SPA (Ember, Vite build) consuming a REST API |
| Language and framework | TypeScript, Ember, `.gts` components, Glint |
| Test framework | QUnit + `@ember/test-helpers`; MSW for the network; Playwright for end-to-end |
| Fast tests | `make web-test-fast` |
| All tests, with end-to-end | `make web-test` |
| Lint and type checks | `make web-lint` |
| Fast-test time budget | Under 90 seconds |
| Where tests live | `tests/unit/`, `tests/integration/`, `tests/acceptance/`, `e2e/` |
| Slow tests | Everything in `e2e/` |
| Expected-failure marker | `test.todo('acceptance: <requirement>', ...)` |
| May be mocked | The HTTP boundary only (MSW). Never the app's own services, components or utils. |

`test.todo` is the strict-xfail equivalent: the run passes while the test
fails, and fails as soon as the test passes, which forces the mark's removal.

### Test levels

| Level | Ember test type | Checks |
|---|---|---|
| Unit | `tests/unit/` | Pure functions in `utils/`, service logic, handlers and builders |
| Integration | `tests/integration/components/` | One component: validation message, disabled submit, role-based visibility, empty and error states |
| Group acceptance | `tests/acceptance/` with MSW | The group's main requirement through real routes and templates |
| End-to-end | `e2e/` with Playwright | One main journey per phase against the real backend |

Business calculations belong to the backend and are tested there. The web
tests that it shows what the API returns and handles 403, 404 and 422.

### Keeping mocks honest

1. `make api-types` regenerates `app/data/types/api.generated.ts` from the
   backend's `openapi.json`.
2. Type every MSW response with those types. A changed contract then fails
   `make web-lint`.
3. The per-phase end-to-end test uses no mocks.

### Test format

```ts
test('member cannot see the close-month button', async function (assert) {
  // GIVEN a logged-in member (not the owner)
  // WHEN  the month summary is rendered
  // THEN  the close-month button is absent
  await render(<template><MonthSummary @role="member" @summary={{summary}} /></template>);
  assert.dom('[data-test-close-month]').doesNotExist();
});
```

Acceptance test skeleton:

```ts
module('Acceptance | log in', function (hooks) {
  setupApplicationTest(hooks);
  setupMsw(hooks);

  test.todo('acceptance: member logs in with a one-time code', async function (assert) {
    worker.use(http.post('/api/v1/auth/verify', () =>
      HttpResponse.json({ success: true, data: { token: 't' } })));

    await visit('/login');
    await fillIn('[data-test-code]', '123456');
    await click('[data-test-submit]');

    assert.strictEqual(currentURL(), '/dashboard');
  });
});
```

---

## 4. Styling (Tailwind CSS v4)

### Setup

Add the Tailwind plugin to the **generated** `vite.config.mjs`, before the Ember
plugins. Keep everything else the blueprint put there.

```js
import tailwindcss from '@tailwindcss/vite';

export default defineConfig({
  plugins: [
    tailwindcss(),
    // ...the plugins the blueprint generated (classicEmberSupport, ember, babel)
  ],
});
```

Add `prettier-plugin-tailwindcss` as the **last** entry in the `plugins` list of
the generated Prettier config, so class order is checked by `make web-format-check`.

With the Vite plugin there is no `tailwind.config.js` and no PostCSS config.
All configuration lives in `app/styles/app.css`.

### Rules

1. **Tokens in one place.** Colours, radius, fonts and shadows are defined with
   `@theme` in `app/styles/app.css`. No hex values or one-off sizes in components.
2. **Utilities live inside `components/ui/`.** `Button`, `Field`, `Card`, `Modal`
   own their class lists. Feature components compose them and add layout
   utilities only (`flex`, `grid`, `gap-*`, spacing).
3. **Variants are args,** mapped to classes in one function inside the component
   (`<Button @variant="danger" @size="sm">`). Callers never pass colour classes.
4. **No `@apply`** outside a few global base styles.
5. **The same class list twice means a missing `ui/` component.** Extract it.
6. **Tests never select by class.** Use `data-test-*`; assert behaviour
   (disabled, visible, text), not styling.
7. **One source of truth for tokens.** If a mobile app shares the design, keep
   the token values in the design spec and mirror them here and in the mobile theme.

### `app/styles/app.css`

```css
@import "tailwindcss";

/* Design tokens. Each one becomes a utility: bg-primary, text-muted, rounded-card ... */
@theme {
  --color-primary: #2563eb;
  --color-primary-hover: #1d4ed8;
  --color-danger: #dc2626;
  --color-danger-hover: #b91c1c;
  --color-surface: #ffffff;
  --color-muted: #64748b;
  --color-border: #e2e8f0;

  --radius-control: 0.5rem;
  --radius-card: 0.75rem;

  --font-sans: "Inter", ui-sans-serif, system-ui, sans-serif;
}

/* Global base styles only. Component styles belong in components/ui. */
@layer base {
  body {
    @apply bg-slate-50 font-sans text-slate-900 antialiased;
  }
}
```

### `app/components/ui/button.gts`

```gts
import type { TOC } from '@ember/component/template-only';

type Variant = 'primary' | 'secondary' | 'danger';
type Size = 'sm' | 'md';

interface ButtonSignature {
  Element: HTMLButtonElement;
  Args: {
    variant?: Variant;
    size?: Size;
    /** Disables the button and marks it busy while a request is running. */
    loading?: boolean;
  };
  Blocks: { default: [] };
}

const BASE =
  'inline-flex items-center justify-center gap-2 rounded-control font-medium ' +
  'transition-colors focus-visible:outline-2 focus-visible:outline-offset-2 ' +
  'focus-visible:outline-primary disabled:cursor-not-allowed disabled:opacity-50';

const VARIANTS: Record<Variant, string> = {
  primary: 'bg-primary text-white hover:bg-primary-hover',
  secondary: 'border border-border bg-surface text-slate-900 hover:bg-slate-50',
  danger: 'bg-danger text-white hover:bg-danger-hover',
};

const SIZES: Record<Size, string> = {
  sm: 'h-8 px-3 text-sm',
  md: 'h-10 px-4 text-sm',
};

function classes(variant: Variant = 'primary', size: Size = 'md'): string {
  return `${BASE} ${VARIANTS[variant]} ${SIZES[size]}`;
}

/**
 * <Button @variant="danger" {{on "click" this.remove}} data-test-remove>Remove</Button>
 * <Button type="submit" @loading={{this.save.isRunning}}>Save</Button>
 */
const Button: TOC<ButtonSignature> = <template>
  <button
    type="button"
    class={{classes @variant @size}}
    disabled={{@loading}}
    aria-busy={{if @loading "true"}}
    ...attributes
  >
    {{yield}}
  </button>
</template>;

export default Button;
```

### `tests/integration/components/ui/button-test.gts`

```gts
import { module, test } from 'qunit';
import { click, render } from '@ember/test-helpers';
import { on } from '@ember/modifier';
import { setupRenderingTest } from '__APP__/tests/helpers';
import Button from '__APP__/components/ui/button';

module('Integration | Component | ui/button', function (hooks) {
  setupRenderingTest(hooks);

  test('it calls the click handler', async function (assert) {
    // GIVEN a button with a click handler
    // WHEN  it is clicked
    // THEN  the handler runs once
    let clicks = 0;
    const handle = () => clicks++;

    await render(
      <template>
        <Button {{on "click" handle}} data-test-save>Save</Button>
      </template>,
    );
    await click('[data-test-save]');

    assert.strictEqual(clicks, 1);
  });

  test('it is disabled while loading', async function (assert) {
    // GIVEN a button whose request is running
    // WHEN  it is rendered with @loading
    // THEN  it is disabled and marked busy
    await render(
      <template><Button @loading={{true}} data-test-save>Save</Button></template>,
    );

    assert.dom('[data-test-save]').isDisabled();
    assert.dom('[data-test-save]').hasAttribute('aria-busy', 'true');
  });
});
```

---

## 5. Starter files

Create each file at the path shown. The handlers and builders have no Ember or
WarpDrive imports, so they are unit-testable on their own.

### `app/data/handlers/types.ts`

```ts
/**
 * Minimal structural types for request handlers.
 *
 * They match the shape WarpDrive's RequestManager expects
 * ({ request(context, next) }), but are declared locally so handlers
 * and their unit tests do not depend on a specific WarpDrive package path.
 */
export interface AppRequest {
  url?: string;
  method?: string;
  headers?: Headers;
  body?: BodyInit | null;
  /** WarpDrive operation name: query, findRecord, createRecord, ... */
  op?: string;
  /** App-specific options. `resourceType` tells the envelope handler what to normalise to. */
  options?: { resourceType?: string; [key: string]: unknown };
  [key: string]: unknown;
}

export interface RequestContext {
  request: AppRequest;
}

export interface StructuredDocument<T> {
  request?: AppRequest;
  response?: Response | null;
  content: T;
}

export type NextFn<T = unknown> = (
  request: AppRequest,
) => Promise<StructuredDocument<T>>;

export interface Handler {
  request<T>(
    context: RequestContext,
    next: NextFn<T>,
  ): Promise<T | StructuredDocument<T>>;
}
```

### `app/data/handlers/errors.ts`

```ts
import type { Handler, NextFn, RequestContext } from './types';

export type ApiErrorKind =
  | 'unauthorized' // 401
  | 'forbidden' // 403
  | 'not-found' // 404
  | 'validation' // 422
  | 'rate-limited' // 429
  | 'server' // 5xx
  | 'network' // no response at all
  | 'unknown';

/** The one error type the rest of the app has to know about. */
export class ApiError extends Error {
  readonly status: number | null;
  readonly kind: ApiErrorKind;
  /** Field name -> messages, filled for 422 responses. */
  readonly fieldErrors: Record<string, string[]>;
  readonly cause?: unknown;

  constructor(
    message: string,
    status: number | null,
    kind: ApiErrorKind,
    fieldErrors: Record<string, string[]> = {},
    cause?: unknown,
  ) {
    super(message);
    this.name = 'ApiError';
    this.status = status;
    this.kind = kind;
    this.fieldErrors = fieldErrors;
    this.cause = cause;
  }
}

export function kindForStatus(status: number | null): ApiErrorKind {
  if (status === null) return 'network';
  if (status === 401) return 'unauthorized';
  if (status === 403) return 'forbidden';
  if (status === 404) return 'not-found';
  if (status === 422) return 'validation';
  if (status === 429) return 'rate-limited';
  if (status >= 500) return 'server';
  return 'unknown';
}

/**
 * Reads FastAPI's 422 body: { detail: [{ loc: ["body", "email"], msg: "..." }] }
 * into { email: ["..."] }. Adjust here if your API reports field errors differently.
 */
export function fieldErrorsFrom(body: unknown): Record<string, string[]> {
  const detail = (body as { detail?: unknown } | null)?.detail;
  if (!Array.isArray(detail)) return {};

  const result: Record<string, string[]> = {};
  for (const item of detail as Array<{ loc?: unknown[]; msg?: string }>) {
    const loc = Array.isArray(item.loc) ? item.loc : [];
    const field = String(loc[loc.length - 1] ?? 'base');
    (result[field] ??= []).push(item.msg ?? 'Invalid value');
  }
  return result;
}

function messageFrom(body: unknown, fallback: string): string {
  const b = body as { message?: unknown; detail?: unknown } | null;
  if (typeof b?.message === 'string') return b.message;
  if (typeof b?.detail === 'string') return b.detail;
  return fallback;
}

/** Converts whatever the network layer throws into an ApiError. Put it first in the handler chain. */
export const ErrorHandler: Handler = {
  async request<T>(context: RequestContext, next: NextFn<T>) {
    try {
      return await next(context.request);
    } catch (error) {
      if (error instanceof ApiError) throw error;

      const e = error as {
        status?: number;
        content?: unknown;
        message?: string;
      } | null;
      const status = typeof e?.status === 'number' ? e.status : null;
      const kind = kindForStatus(status);

      throw new ApiError(
        messageFrom(e?.content, e?.message ?? 'Request failed'),
        status,
        kind,
        kind === 'validation' ? fieldErrorsFrom(e?.content) : {},
        error,
      );
    }
  },
};
```

### `app/data/handlers/auth.ts`

```ts
import type { Handler, NextFn, RequestContext } from './types';

/**
 * Adds the bearer token to every request and reports 401s.
 * (This is the header half of what an Adapter used to do.)
 *
 * @param getToken        returns the current token, or null when logged out
 * @param onUnauthorized  called when the API answers 401 (e.g. session.invalidate)
 */
export function createAuthHandler(
  getToken: () => string | null,
  onUnauthorized?: () => void,
): Handler {
  return {
    async request<T>(context: RequestContext, next: NextFn<T>) {
      const headers = new Headers(context.request.headers);
      headers.set('Accept', 'application/json');

      const token = getToken();
      if (token) {
        headers.set('Authorization', `Bearer ${token}`);
      }

      try {
        return await next({ ...context.request, headers });
      } catch (error) {
        if ((error as { status?: number } | null)?.status === 401) {
          onUnauthorized?.();
        }
        throw error;
      }
    },
  };
}
```

### `app/data/handlers/api-envelope.ts`

```ts
import type { Handler, NextFn, RequestContext } from './types';

/**
 * Converts the backend's response envelope into the JSON:API shape the
 * store cache understands. (This is what a Serializer used to do.)
 *
 * Default envelope:  { success, message, data, meta? }
 * This is the ONLY file that knows the envelope shape. If your API differs,
 * pass your own `unwrap`.
 */
export interface Unwrapped {
  data: unknown;
  meta?: Record<string, unknown>;
}

export interface EnvelopeOptions {
  unwrap?: (body: unknown) => Unwrapped;
  /** Name of the primary key field in API payloads. Default: "id". */
  idField?: string;
}

export interface JsonApiResource {
  type: string;
  id: string;
  attributes: Record<string, unknown>;
}

export function defaultUnwrap(body: unknown): Unwrapped {
  if (body !== null && typeof body === 'object' && 'data' in body) {
    const b = body as { data: unknown; meta?: Record<string, unknown> };
    return { data: b.data, meta: b.meta };
  }
  return { data: body };
}

export function toResource(
  type: string,
  raw: Record<string, unknown>,
  idField = 'id',
): JsonApiResource {
  const { [idField]: id, ...attributes } = raw;
  return { type, id: String(id), attributes };
}

export function createEnvelopeHandler(options: EnvelopeOptions = {}): Handler {
  const unwrap = options.unwrap ?? defaultUnwrap;
  const idField = options.idField ?? 'id';

  return {
    async request<T>(context: RequestContext, next: NextFn<T>) {
      const doc = await next(context.request);
      const { data, meta } = unwrap(doc.content);
      const type = context.request.options?.resourceType;

      // No resource type: the caller wants the plain payload (e.g. login, reports).
      if (!type) return data as T;

      // Nothing to normalise (e.g. DELETE with an empty body).
      if (data === null || data === undefined) {
        return { meta: meta ?? {} } as T;
      }

      const normalised = Array.isArray(data)
        ? data.map((item) =>
            toResource(type, item as Record<string, unknown>, idField),
          )
        : toResource(type, data as Record<string, unknown>, idField);

      return (meta ? { data: normalised, meta } : { data: normalised }) as T;
    },
  };
}
```

### `app/data/config.ts`

```ts
/**
 * Where the API lives. Set VITE_API_HOST in .env.development / .env.production.
 * Leave it empty to call the same origin (useful behind a reverse proxy).
 */
const env = (import.meta as { env?: Record<string, string | undefined> }).env;

export const API_HOST = env?.['VITE_API_HOST'] ?? '';
export const API_NAMESPACE = '/api/v1';

export function apiUrl(path: string): string {
  return `${API_HOST}${API_NAMESPACE}/${path.replace(/^\/+/, '')}`;
}
```

### `app/data/builders/resource.ts`

```ts
import { apiUrl } from '../config';
import type { AppRequest } from '../handlers/types';

/**
 * Request builders for a REST resource. (This is the URL half of what an
 * Adapter used to do.) Builders only describe a request; `store.request(...)`
 * sends it.
 *
 * Usage, one small file per resource:
 *
 *   // app/data/builders/meals.ts
 *   export const meals = resourceBuilders('meal', 'meals');
 *
 *   // in a route
 *   const { content } = await this.store.request(meals.list({ month: '2026-10' }));
 */
export type QueryParams = Record<
  string,
  string | number | boolean | null | undefined
>;

export function withQuery(url: string, params?: QueryParams): string {
  if (!params) return url;
  const search = new URLSearchParams();
  // Sorted so the same query always produces the same URL (= the same cache key).
  for (const key of Object.keys(params).sort()) {
    const value = params[key];
    if (value !== null && value !== undefined) search.set(key, String(value));
  }
  const qs = search.toString();
  return qs ? `${url}?${qs}` : url;
}

function json(body: unknown): { body: string; headers: Headers } {
  return {
    body: JSON.stringify(body),
    headers: new Headers({ 'Content-Type': 'application/json' }),
  };
}

export function resourceBuilders(resourceType: string, path: string) {
  const options = { resourceType };

  return {
    list(params?: QueryParams): AppRequest {
      return {
        url: withQuery(apiUrl(path), params),
        method: 'GET',
        op: 'query',
        options,
      };
    },

    detail(id: string | number): AppRequest {
      return {
        url: apiUrl(`${path}/${id}`),
        method: 'GET',
        op: 'findRecord',
        options,
      };
    },

    create(attributes: Record<string, unknown>): AppRequest {
      return {
        url: apiUrl(path),
        method: 'POST',
        op: 'createRecord',
        options,
        ...json(attributes),
      };
    },

    update(id: string | number, attributes: Record<string, unknown>): AppRequest {
      return {
        url: apiUrl(`${path}/${id}`),
        method: 'PATCH',
        op: 'updateRecord',
        options,
        ...json(attributes),
      };
    },

    remove(id: string | number): AppRequest {
      return {
        url: apiUrl(`${path}/${id}`),
        method: 'DELETE',
        op: 'deleteRecord',
        options,
      };
    },
  };
}
```

### `app/data/lifetimes.ts`

```ts
/**
 * Cache policy in one place.
 *
 * soft: after this long, show cached data and refresh in the background.
 * hard: after this long, wait for a fresh response.
 *
 * Pass these to the store's cache policy (see store.example.ts). For data that
 * never changes once written (closed periods, archived records), use a builder
 * option or a longer policy instead of lowering these defaults.
 */
export const CACHE_SOFT_EXPIRES_MS = 30 * 1000;
export const CACHE_HARD_EXPIRES_MS = 5 * 60 * 1000;
```

### `app/data/store.example.ts`

```ts
/**
 * HOW TO WIRE THE HANDLERS INTO THE STORE
 *
 * This file is an example, not live code. `ember new` already generates
 * app/services/store.ts; edit THAT file and add the three handlers.
 * WarpDrive's import paths have changed between releases, so match whatever
 * your generated store imports and check https://docs.warp-drive.io.
 *
 * Handler order matters: errors -> auth -> envelope -> (network).
 *
 * ── Variant A: generated store uses `useLegacyStore` (recent blueprints) ──
 *
 *   import { useLegacyStore } from '@warp-drive/legacy';
 *   import { JSONAPICache } from '@warp-drive/json-api';
 *   import { ErrorHandler } from '../data/handlers/errors';
 *   import { createAuthHandler } from '../data/handlers/auth';
 *   import { createEnvelopeHandler } from '../data/handlers/api-envelope';
 *   import { readToken, clearToken } from './session';
 *
 *   const Store = useLegacyStore({
 *     linksMode: false,
 *     cache: JSONAPICache,
 *     handlers: [
 *       ErrorHandler,
 *       createAuthHandler(readToken, clearToken),
 *       createEnvelopeHandler(),
 *     ],
 *     schemas: [],
 *   });
 *   export default Store;
 *
 * ── Variant B: store class with an explicit RequestManager ──
 *
 *   import Store, { CacheHandler } from '@ember-data/store';
 *   import RequestManager from '@ember-data/request';
 *   import Fetch from '@ember-data/request/fetch';
 *
 *   export default class AppStore extends Store {
 *     requestManager = new RequestManager()
 *       .use([
 *         ErrorHandler,
 *         createAuthHandler(readToken, clearToken),
 *         createEnvelopeHandler(),
 *         Fetch,
 *       ])
 *       .useCache(CacheHandler);
 *   }
 *
 * Cache lifetimes: configure the store's cache policy with the values in
 * ../data/lifetimes.ts (the option is named `policy` / `lifetimes` depending
 * on the WarpDrive version).
 */
export {};
```

### `app/services/session.ts`

```ts
import Service from '@ember/service';
import { tracked } from '@glimmer/tracking';

const STORAGE_KEY = 'session-token';

/** Storage can throw (private mode, blocked cookies), so every access is guarded. */
export function readToken(): string | null {
  try {
    return localStorage.getItem(STORAGE_KEY);
  } catch {
    return null;
  }
}

export function writeToken(token: string): void {
  try {
    localStorage.setItem(STORAGE_KEY, token);
  } catch {
    // Session then lasts until the page reloads.
  }
}

export function clearToken(): void {
  try {
    localStorage.removeItem(STORAGE_KEY);
  } catch {
    // Nothing to clear.
  }
}

/**
 * Minimal token session. Swap for ember-simple-auth if you need refresh
 * tokens, multiple authenticators or cross-tab sync.
 */
export default class SessionService extends Service {
  @tracked token: string | null = readToken();

  get isAuthenticated(): boolean {
    return this.token !== null;
  }

  authenticate(token: string): void {
    writeToken(token);
    this.token = token;
  }

  invalidate(): void {
    clearToken();
    this.token = null;
  }
}

declare module '@ember/service' {
  interface Registry {
    session: SessionService;
  }
}
```

### `app/routes/authenticated.ts`

```ts
import Route from '@ember/routing/route';
import { service } from '@ember/service';
import type RouterService from '@ember/routing/router-service';
import type SessionService from '../services/session';

/**
 * Parent route for everything behind login. The guard lives here once;
 * child routes never check authentication themselves.
 *
 * router.ts:
 *   this.route('login');
 *   this.route('authenticated', { path: '' }, function () {
 *     this.route('dashboard');
 *   });
 */
export default class AuthenticatedRoute extends Route {
  @service declare session: SessionService;
  @service declare router: RouterService;

  beforeModel(): void {
    if (!this.session.isAuthenticated) {
      this.router.replaceWith('login');
    }
  }
}
```

### `tests/helpers/msw.ts`

```ts
import { setupWorker } from 'msw/browser';
import type { RequestHandler } from 'msw';

/**
 * Network mocking for fast tests. MSW intercepts fetch at the network
 * boundary, so the real store, handlers, routes and components all run.
 *
 *   module('Acceptance | login', function (hooks) {
 *     setupApplicationTest(hooks);
 *     setupMsw(hooks);
 *
 *     test('...', async function (assert) {
 *       worker.use(http.post('/api/v1/auth/verify', () => HttpResponse.json({ ... })));
 *     });
 *   });
 *
 * Type the handler payloads with app/data/types/api.generated.ts so a changed
 * API contract fails the type check instead of silently passing.
 */
export const worker = setupWorker();

let started: Promise<unknown> | null = null;

export function setupMsw(
  hooks: NestedHooks,
  ...defaultHandlers: RequestHandler[]
): void {
  hooks.before(async function () {
    started ??= worker.start({
      quiet: true,
      onUnhandledRequest(request, print) {
        // An unmocked API call is a test bug; asset requests are fine.
        if (new URL(request.url).pathname.startsWith('/api')) {
          print.error();
        }
      },
    });
    await started;
  });

  hooks.beforeEach(function () {
    worker.use(...defaultHandlers);
  });

  hooks.afterEach(function () {
    worker.resetHandlers();
  });
}
```

### `tests/helpers/login.ts`

```ts
import { clearToken, writeToken } from '__APP__/services/session';

/**
 * Puts a fake token in storage before the app boots, so application tests
 * start behind the login guard.
 *
 *   setupApplicationTest(hooks);
 *   setupLoggedIn(hooks);
 */
export function setupLoggedIn(hooks: NestedHooks, token = 'test-token'): void {
  hooks.beforeEach(function () {
    writeToken(token);
  });

  hooks.afterEach(function () {
    clearToken();
  });
}
```

### `tests/unit/data/handlers-test.ts`

```ts
import { module, test } from 'qunit';
import { createAuthHandler } from '__APP__/data/handlers/auth';
import { createEnvelopeHandler } from '__APP__/data/handlers/api-envelope';
import { ApiError, ErrorHandler } from '__APP__/data/handlers/errors';
import type { AppRequest, NextFn } from '__APP__/data/handlers/types';

function respondWith<T>(content: T): NextFn<T> {
  return (request) => Promise.resolve({ request, content });
}

function failWith(status: number, content: unknown): NextFn<never> {
  return () =>
    Promise.reject(
      Object.assign(new Error('Request failed'), { status, content }),
    );
}

module('Unit | Data | handlers', function () {
  test('auth handler sends the bearer token', async function (assert) {
    // GIVEN a logged-in session
    // WHEN  a request passes through the auth handler
    // THEN  it carries the Authorization header
    let seen: AppRequest | undefined;
    const handler = createAuthHandler(() => 'abc');

    await handler.request({ request: { url: '/x' } }, (request) => {
      seen = request;
      return Promise.resolve({ content: null });
    });

    assert.strictEqual(seen?.headers?.get('Authorization'), 'Bearer abc');
  });

  test('auth handler reports a 401', async function (assert) {
    // GIVEN an expired token
    // WHEN  the API answers 401
    // THEN  onUnauthorized is called and the error still propagates
    let called = 0;
    const handler = createAuthHandler(
      () => 'old',
      () => called++,
    );

    await assert.rejects(
      handler.request({ request: { url: '/x' } }, failWith(401, null)),
    );
    assert.strictEqual(called, 1);
  });

  test('envelope handler normalises a list to JSON:API resources', async function (assert) {
    // GIVEN an enveloped list response
    // WHEN  it passes through the envelope handler with a resource type
    // THEN  each item becomes { type, id, attributes }
    const handler = createEnvelopeHandler();

    const result = await handler.request(
      { request: { options: { resourceType: 'meal' } } },
      respondWith({ success: true, data: [{ id: 7, count: 2 }] }),
    );

    assert.deepEqual(result, {
      data: [{ type: 'meal', id: '7', attributes: { count: 2 } }],
    });
  });

  test('envelope handler returns the plain payload without a resource type', async function (assert) {
    // GIVEN an enveloped non-resource response (e.g. login)
    // WHEN  it passes through the envelope handler
    // THEN  only the inner data is returned
    const handler = createEnvelopeHandler();

    const result = await handler.request(
      { request: {} },
      respondWith({ success: true, data: { token: 't' } }),
    );

    assert.deepEqual(result, { token: 't' });
  });

  test('error handler maps a 422 to field errors', async function (assert) {
    // GIVEN a FastAPI validation error body
    // WHEN  the request fails with 422
    // THEN  an ApiError of kind "validation" carries messages per field
    const body = { detail: [{ loc: ['body', 'email'], msg: 'Invalid email' }] };

    try {
      await ErrorHandler.request({ request: {} }, failWith(422, body));
      assert.ok(false, 'expected the request to fail');
    } catch (error) {
      assert.true(error instanceof ApiError);
      const e = error as ApiError;
      assert.strictEqual(e.kind, 'validation');
      assert.deepEqual(e.fieldErrors, { email: ['Invalid email'] });
    }
  });

  test('error handler maps a failed fetch to a network error', async function (assert) {
    // GIVEN no response from the server
    // WHEN  the request rejects without a status
    // THEN  an ApiError of kind "network" is thrown
    const next: NextFn<never> = () => Promise.reject(new TypeError('Failed to fetch'));

    try {
      await ErrorHandler.request({ request: {} }, next);
      assert.ok(false, 'expected the request to fail');
    } catch (error) {
      assert.strictEqual((error as ApiError).kind, 'network');
    }
  });
});
```

### `tests/unit/data/builders-test.ts`

```ts
import { module, test } from 'qunit';
import { resourceBuilders, withQuery } from '__APP__/data/builders/resource';

module('Unit | Data | builders', function () {
  test('list builds a GET with sorted query params', function (assert) {
    // GIVEN builders for a resource
    // WHEN  a list request is built with params in any order
    // THEN  the URL is stable, so it works as a cache key
    const meals = resourceBuilders('meal', 'meals');

    const request = meals.list({ month: '2026-10', home: 1 });

    assert.strictEqual(request.method, 'GET');
    assert.true(request.url?.endsWith('/api/v1/meals?home=1&month=2026-10'));
    assert.strictEqual(request.options?.resourceType, 'meal');
  });

  test('create builds a JSON POST', function (assert) {
    // GIVEN builders for a resource
    // WHEN  a create request is built
    // THEN  it posts the attributes as JSON
    const meals = resourceBuilders('meal', 'meals');

    const request = meals.create({ count: 2 });

    assert.strictEqual(request.method, 'POST');
    assert.strictEqual(request.body, '{"count":2}');
    assert.strictEqual(request.headers?.get('Content-Type'), 'application/json');
  });

  test('withQuery skips empty values', function (assert) {
    // GIVEN params containing null and undefined
    // WHEN  the query string is built
    // THEN  only real values appear
    assert.strictEqual(withQuery('/x', { a: null, b: undefined, c: 0 }), '/x?c=0');
  });
});
```

### `e2e/smoke.spec.ts`

```ts
import { expect, test } from '@playwright/test';

/**
 * End-to-end tests run against the real backend (docker compose up) with no
 * mocks. Keep them few: one main journey per phase.
 */
test('the app boots', async ({ page }) => {
  // GIVEN the web app and API are running
  // WHEN  a visitor opens the home page
  // THEN  the application renders
  await page.goto('/');
  await expect(page.locator('body')).toBeVisible();
});
```

### `playwright.config.ts`

```ts
import { defineConfig, devices } from '@playwright/test';

export default defineConfig({
  testDir: './e2e',
  fullyParallel: false,
  retries: process.env['CI'] ? 1 : 0,
  reporter: process.env['CI'] ? 'line' : 'list',
  use: {
    baseURL: process.env['WEB_URL'] ?? 'http://localhost:4200',
    trace: 'retain-on-failure',
  },
  projects: [{ name: 'chromium', use: { ...devices['Desktop Chrome'] } }],
  // Starts the dev server for local runs. The API must already be up.
  webServer: {
    command: 'pnpm start',
    url: 'http://localhost:4200',
    reuseExistingServer: true,
    timeout: 120_000,
  },
});
```

### `Makefile`

```makefile
# Web targets. Wraps the scripts the Ember blueprint generates in package.json.
OPENAPI_URL ?= http://localhost:8000/openapi.json

.PHONY: web-test-fast web-e2e web-test web-lint web-format-check api-types

web-test-fast: ## unit + integration + acceptance (mocked network)
	pnpm test

web-e2e: ## Playwright against the real backend (slow)
	pnpm exec playwright test

web-test: web-test-fast web-e2e ## everything

web-lint: ## ESLint, template lint, type check (as defined by the blueprint)
	pnpm lint

web-format-check:
	pnpm exec prettier --check .

api-types: ## regenerate API types from the backend OpenAPI schema
	pnpm exec openapi-typescript $(OPENAPI_URL) -o app/data/types/api.generated.ts
```

### `.env.example`

```bash
# Copy to .env.development and .env.production.
# Leave empty to call the API on the same origin.
VITE_API_HOST=http://localhost:8000
```

---

## 6. After setup checklist

- [ ] **Wire the store.** Add `ErrorHandler`, the auth handler and the envelope
      handler to the generated `app/services/store.ts`, following
      `app/data/store.example.ts`. WarpDrive's import paths differ between
      blueprint versions, so match what the generated store imports and check
      https://docs.warp-drive.io.
- [ ] **Match the envelope.** If the API does not return
      `{ success, message, data, meta? }`, pass a custom `unwrap` to
      `createEnvelopeHandler`.
- [ ] **Fix test imports.** Replace `__APP__` with the app name. If the generated
      tests use another alias (for example `#app/`), use that instead.
- [ ] **Add the routes.** `login` plus the `authenticated` parent route in `router.ts`.
- [ ] **Enable Tailwind.** Add `tailwindcss()` to the generated Vite config and
      create `app/styles/app.css` from section 4. Replace the sample token
      values with the project's design tokens.
- [ ] **Add ESLint boundaries** from section 2.
- [ ] **Set `VITE_API_HOST`** in `.env.development` and `.env.production`.
- [ ] **Run `make web-test-fast`.** The starter unit tests should pass.
- [ ] **Run `make api-types`** once the backend serves `openapi.json`.

## Status of this template

The handlers and builders were type-checked and their behaviour verified. The
Ember-dependent files (session service, route guard, `ui/button` and its test),
the Tailwind setup, the MSW helper and the Playwright config have not been run inside a generated app; expect small
adjustments on first use.