# E2E / System Tests

BDD system tests with [Playwright](https://playwright.dev) and [playwright-bdd](https://vitalets.github.io/playwright-bdd/).

```bash
cd e2e
npm install
npx playwright install chromium   # only needed for UI scenarios
npm test                          # backend must be running on :8000
```

- `features/`: Gherkin scenarios, tagged with their test case (`@TC-xxx`) or business rule (`@BR-xx`).
- `steps/`: step definitions. `pages/`: Page Objects (selectors use `data-testid`).
- Scenarios tagged `@wip` wait for the frontend or the API and are skipped. Remove the tag once their steps exist.
- `API_URL` and `BASE_URL` override the default backend (`http://127.0.0.1:8000`) and frontend (`http://localhost:5173`).
