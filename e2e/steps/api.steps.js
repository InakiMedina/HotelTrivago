import { expect } from '@playwright/test';
import { When, Then, API_URL } from './fixtures.js';

When('I send GET {string} to the backend', async ({ request, ctx }, path) => {
  ctx.response = await request.get(`${API_URL}${path}`);
});

Then('the response status is {int}', async ({ ctx }, status) => {
  expect(ctx.response.status()).toBe(status);
});

Then('the response field {string} is {string}', async ({ ctx }, field, value) => {
  expect((await ctx.response.json())[field]).toBe(value);
});
