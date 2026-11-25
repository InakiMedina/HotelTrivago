// Base Page Object. Portal pages (login, search, room detail, employee) extend it
// once the frontend exists. Selectors use data-testid.
export class BasePage {
  constructor(page) {
    this.page = page;
  }

  async open(path) {
    await this.page.goto(path);
  }

  byTestId(id) {
    return this.page.getByTestId(id);
  }
}
