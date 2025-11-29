import { describe, it, expect, beforeAll, afterAll } from 'vitest';
import puppeteer, { Browser, Page } from 'puppeteer';

const BASE_URL = process.env.VITE_APP_URL || 'http://localhost:3000';

describe('Responsive Design E2E Tests', () => {
  let browser: Browser;
  let page: Page;

  beforeAll(async () => {
    browser = await puppeteer.launch({
      headless: true,
      args: ['--no-sandbox', '--disable-setuid-sandbox'],
    });
  });

  afterAll(async () => {
    await browser.close();
  });

  describe('Mobile Viewport (375x667 - iPhone SE)', () => {
    beforeAll(async () => {
      page = await browser.newPage();
      await page.setViewport({ width: 375, height: 667 });
    });

    it('should not have horizontal scroll', async () => {
      await page.goto(BASE_URL, { waitUntil: 'networkidle2' });

      const bodyWidth = await page.evaluate(() => document.body.scrollWidth);
      const viewportWidth = await page.evaluate(() => window.innerWidth);

      expect(bodyWidth).toBeLessThanOrEqual(viewportWidth);
    });

    it('should display mobile navigation menu button', async () => {
      await page.goto(BASE_URL, { waitUntil: 'networkidle2' });

      const mobileMenuButton = await page.$('[aria-label="Toggle menu"]');
      expect(mobileMenuButton).toBeTruthy();

      const isVisible = await page.evaluate((el) => {
        if (!el) return false;
        const style = window.getComputedStyle(el);
        return style.display !== 'none' && style.visibility !== 'hidden';
      }, mobileMenuButton);

      expect(isVisible).toBe(true);
    });

    it('should toggle mobile menu on button click', async () => {
      await page.goto(BASE_URL, { waitUntil: 'networkidle2' });

      // Click mobile menu button
      await page.click('[aria-label="Toggle menu"]');
      await page.waitForTimeout(300); // Wait for animation

      // Check if menu is expanded
      const isExpanded = await page.$eval(
        '[aria-label="Toggle menu"]',
        (el) => el.getAttribute('aria-expanded') === 'true'
      );

      expect(isExpanded).toBe(true);
    });

    it('should have touch-friendly button sizes (min 44px)', async () => {
      await page.goto(BASE_URL, { waitUntil: 'networkidle2' });

      const buttons = await page.$$('button');
      expect(buttons.length).toBeGreaterThan(0);

      for (const button of buttons) {
        const box = await button.boundingBox();
        if (box) {
          // Check minimum touch target size
          expect(box.height).toBeGreaterThanOrEqual(44);
          expect(box.width).toBeGreaterThanOrEqual(44);
        }
      }
    });

    it('should display filter drawer instead of sidebar', async () => {
      await page.goto(BASE_URL, { waitUntil: 'networkidle2' });

      // Desktop filter sidebar should be hidden
      const desktopSidebar = await page.$('aside.hidden.lg\\:block');
      const isHidden = await page.evaluate((el) => {
        if (!el) return true;
        const style = window.getComputedStyle(el);
        return style.display === 'none';
      }, desktopSidebar);

      expect(isHidden).toBe(true);

      // Mobile filter button should be visible
      const mobileFilterButton = await page.$('button:has-text("Filters")');
      expect(mobileFilterButton).toBeTruthy();
    });

    it('should not show carousel navigation arrows on mobile', async () => {
      await page.goto(`${BASE_URL}/recipes/1`, { waitUntil: 'networkidle2' });

      // Wait for similar recipes to load
      await page.waitForTimeout(1000);

      // Check if carousel arrows are hidden
      const leftArrow = await page.$('[aria-label="Scroll left"]');
      const rightArrow = await page.$('[aria-label="Scroll right"]');

      const leftArrowVisible = leftArrow
        ? await page.evaluate((el) => {
            const style = window.getComputedStyle(el);
            return style.display !== 'none' && style.visibility !== 'hidden';
          }, leftArrow)
        : false;

      const rightArrowVisible = rightArrow
        ? await page.evaluate((el) => {
            const style = window.getComputedStyle(el);
            return style.display !== 'none' && style.visibility !== 'hidden';
          }, rightArrow)
        : false;

      // On mobile, arrows should be hidden (touch gestures used instead)
      expect(leftArrowVisible).toBe(false);
      expect(rightArrowVisible).toBe(false);
    });
  });

  describe('Small Mobile Viewport (320x568 - iPhone 5/SE)', () => {
    beforeAll(async () => {
      page = await browser.newPage();
      await page.setViewport({ width: 320, height: 568 });
    });

    it('should not have horizontal scroll on smallest viewport', async () => {
      await page.goto(BASE_URL, { waitUntil: 'networkidle2' });

      const bodyWidth = await page.evaluate(() => document.body.scrollWidth);
      const viewportWidth = await page.evaluate(() => window.innerWidth);

      expect(bodyWidth).toBeLessThanOrEqual(viewportWidth);
    });

    it('should display content without overflow', async () => {
      await page.goto(BASE_URL, { waitUntil: 'networkidle2' });

      const hasOverflow = await page.evaluate(() => {
        return document.documentElement.scrollWidth > window.innerWidth;
      });

      expect(hasOverflow).toBe(false);
    });
  });

  describe('Tablet Viewport (768x1024 - iPad)', () => {
    beforeAll(async () => {
      page = await browser.newPage();
      await page.setViewport({ width: 768, height: 1024 });
    });

    it('should not have horizontal scroll', async () => {
      await page.goto(BASE_URL, { waitUntil: 'networkidle2' });

      const bodyWidth = await page.evaluate(() => document.body.scrollWidth);
      const viewportWidth = await page.evaluate(() => window.innerWidth);

      expect(bodyWidth).toBeLessThanOrEqual(viewportWidth);
    });

    it('should show desktop navigation on tablet', async () => {
      await page.goto(BASE_URL, { waitUntil: 'networkidle2' });

      // Desktop navigation should be visible
      const desktopNav = await page.$('nav.hidden.md\\:flex');
      const isVisible = await page.evaluate((el) => {
        if (!el) return false;
        const style = window.getComputedStyle(el);
        return style.display !== 'none';
      }, desktopNav);

      expect(isVisible).toBe(true);
    });
  });

  describe('Desktop Viewport (1920x1080)', () => {
    beforeAll(async () => {
      page = await browser.newPage();
      await page.setViewport({ width: 1920, height: 1080 });
    });

    it('should not have horizontal scroll', async () => {
      await page.goto(BASE_URL, { waitUntil: 'networkidle2' });

      const bodyWidth = await page.evaluate(() => document.body.scrollWidth);
      const viewportWidth = await page.evaluate(() => window.innerWidth);

      expect(bodyWidth).toBeLessThanOrEqual(viewportWidth);
    });

    it('should show desktop layout with sidebar', async () => {
      await page.goto(BASE_URL, { waitUntil: 'networkidle2' });

      // Desktop filter sidebar should be visible
      const desktopSidebar = await page.$('aside.hidden.lg\\:block');
      const isVisible = await page.evaluate((el) => {
        if (!el) return false;
        const style = window.getComputedStyle(el);
        return style.display !== 'none';
      }, desktopSidebar);

      expect(isVisible).toBe(true);
    });

    it('should show carousel navigation arrows on desktop', async () => {
      await page.goto(`${BASE_URL}/recipes/1`, { waitUntil: 'networkidle2' });

      // Wait for similar recipes to load
      await page.waitForTimeout(1000);

      // Desktop should show carousel arrows
      const leftArrow = await page.$('[aria-label="Scroll left"]');
      const rightArrow = await page.$('[aria-label="Scroll right"]');

      // At least one arrow should be visible (right arrow typically visible at start)
      expect(leftArrow || rightArrow).toBeTruthy();
    });

    it('should hide mobile menu button on desktop', async () => {
      await page.goto(BASE_URL, { waitUntil: 'networkidle2' });

      const mobileMenuButton = await page.$('[aria-label="Toggle menu"]');
      const isVisible = await page.evaluate((el) => {
        if (!el) return false;
        const style = window.getComputedStyle(el);
        return style.display !== 'none' && style.visibility !== 'hidden';
      }, mobileMenuButton);

      expect(isVisible).toBe(false);
    });
  });

  describe('Form Responsiveness', () => {
    beforeAll(async () => {
      page = await browser.newPage();
    });

    it('should have accessible input sizes on mobile (375x667)', async () => {
      await page.setViewport({ width: 375, height: 667 });
      await page.goto(`${BASE_URL}/recipes/new`, { waitUntil: 'networkidle2' });

      const inputs = await page.$$('input[type="text"], textarea, select');

      for (const input of inputs) {
        const box = await input.boundingBox();
        if (box) {
          // Minimum touch target height
          expect(box.height).toBeGreaterThanOrEqual(44);
        }

        // Font size should be at least 16px to prevent iOS zoom
        const fontSize = await page.evaluate((el) => {
          return parseInt(window.getComputedStyle(el).fontSize, 10);
        }, input);

        expect(fontSize).toBeGreaterThanOrEqual(16);
      }
    });

    it('should stack form fields vertically on mobile', async () => {
      await page.setViewport({ width: 375, height: 667 });
      await page.goto(`${BASE_URL}/recipes/new`, { waitUntil: 'networkidle2' });

      // Check that form uses full width on mobile
      const form = await page.$('form');
      if (form) {
        const width = await page.evaluate((el) => {
          return el.getBoundingClientRect().width;
        }, form);

        const viewportWidth = await page.evaluate(() => window.innerWidth);

        // Form should use most of viewport width (accounting for padding)
        expect(width).toBeGreaterThan(viewportWidth * 0.8);
      }
    });
  });

  describe('Modal Responsiveness', () => {
    beforeAll(async () => {
      page = await browser.newPage();
    });

    it('should display modals properly on mobile (375x667)', async () => {
      await page.setViewport({ width: 375, height: 667 });
      await page.goto(BASE_URL, { waitUntil: 'networkidle2' });

      // Try to open filter drawer on mobile
      const filterButton = await page.$('button');
      if (filterButton) {
        const buttonText = await page.evaluate(
          (el) => el.textContent,
          filterButton
        );

        if (buttonText?.includes('Filter')) {
          await filterButton.click();
          await page.waitForTimeout(300);

          // Check that drawer doesn't overflow viewport
          const drawer = await page.$('div[class*="fixed"]');
          if (drawer) {
            const box = await drawer.boundingBox();
            if (box) {
              expect(box.width).toBeLessThanOrEqual(375);
              expect(box.height).toBeLessThanOrEqual(667);
            }
          }
        }
      }
    });
  });
});
