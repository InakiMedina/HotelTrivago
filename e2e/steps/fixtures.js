import { test as base, createBdd } from 'playwright-bdd';
import { BasePage } from '../pages/BasePage.js';

export const API_URL = process.env.API_URL ?? 'http://127.0.0.1:8000';

export const test = base.extend({
  // Shared state between the steps of one scenario.
  ctx: async ({}, use) => use({}),
  basePage: async ({ page }, use) => use(new BasePage(page)),
});

export const { Given, When, Then } = createBdd(test);
