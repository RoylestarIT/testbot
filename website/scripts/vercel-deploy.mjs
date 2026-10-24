import { chromium } from "playwright";
import { mkdirSync, writeFileSync } from "fs";

const IMPORT_URL =
  "https://vercel.com/new/import?s=https%3A%2F%2Fgithub.com%2FRoylestarIT%2Ftestbot&root-directory=website&project-name=golos-brenda";
const USER_DATA = process.env.CHROME_USER_DATA || "/home/ubuntu/.config/google-chrome";
const OUT = "/tmp/vercel-deploy";

async function sleep(ms) {
  return new Promise((r) => setTimeout(r, ms));
}

async function snap(page, name) {
  try {
    await page.screenshot({ path: `${OUT}/${name}.png`, fullPage: true });
    writeFileSync(`${OUT}/${name}.url.txt`, page.url());
    writeFileSync(`${OUT}/${name}.html`, (await page.content()).slice(0, 200000));
  } catch {
    /* ignore */
  }
}

async function main() {
  mkdirSync(OUT, { recursive: true });
  const browser = await chromium.launchPersistentContext(USER_DATA, {
    channel: "chrome",
    headless: false,
    args: ["--no-sandbox", "--disable-dev-shm-usage", "--password-store=basic"],
    viewport: { width: 1400, height: 900 },
  });

  try {
    const page = browser.pages()[0] ?? (await browser.newPage());
    await page.goto(IMPORT_URL, { waitUntil: "domcontentloaded", timeout: 120000 });
    await snap(page, "01-import");

    if (/login|sign in/i.test(await page.title())) {
      console.log(JSON.stringify({ error: "not_logged_in", url: page.url() }));
      return;
    }

    for (const label of [/Install/, /Authorize/, /Continue with GitHub/, /Connect/]) {
      const btn = page.getByRole("button", { name: label }).first();
      if (await btn.isVisible().catch(() => false)) {
        await btn.click();
        await sleep(6000);
        await snap(page, "02-auth");
      }
    }

    const repoLink = page.locator('a, button, [role="button"]').filter({ hasText: /testbot/i }).first();
    if (await repoLink.isVisible().catch(() => false)) {
      await repoLink.click();
      await sleep(4000);
      await snap(page, "03-repo");
    }

    const inputs = page.locator("input");
    const count = await inputs.count();
    for (let i = 0; i < count; i++) {
      const el = inputs.nth(i);
      const ph = (await el.getAttribute("placeholder")) || "";
      const name = (await el.getAttribute("name")) || "";
      if (/root|directory/i.test(ph + name)) {
        await el.fill("website");
        break;
      }
    }

    const deploy = page.getByRole("button", { name: /^(Deploy|Create|Import)$/i }).first();
    if (await deploy.isVisible().catch(() => false)) {
      await deploy.click();
      await snap(page, "04-deploy-click");
    }

    let productionUrl = "";
    for (let i = 0; i < 120; i++) {
      await sleep(4000);
      try {
        const body = await page.content();
        const m = body.match(/https:\/\/[a-z0-9-]+\.vercel\.app/gi);
        if (m?.length) productionUrl = [...new Set(m)][0];
        if (/Congratulations|Deployment ready|Ready/i.test(body)) break;
        if (page.url().includes("/dashboard/")) break;
      } catch {
        break;
      }
    }

    await snap(page, "05-final");
    console.log(JSON.stringify({ productionUrl, finalUrl: page.url() }, null, 2));
  } finally {
    await browser.close();
  }
}

main().catch((e) => {
  console.error(e);
  process.exit(1);
});
