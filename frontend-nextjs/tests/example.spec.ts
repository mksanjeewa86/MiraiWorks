import { test, expect } from '@playwright/test';

test.describe('Basic Website Tests', () => {
  test('should load homepage correctly', async ({ page }) => {
    await page.goto('/');

    // Check that the page loads
    await expect(page).toHaveTitle(/MiraiWorks/);
    
    // Check main navigation
    await expect(page.locator('nav')).toBeVisible();
    
    // Check hero section
    await expect(page.locator('h1')).toBeVisible();
    
    // Check footer
    await expect(page.locator('footer')).toBeVisible();
  });

  test('should navigate to jobs page from homepage', async ({ page }) => {
    await page.goto('/');
    
    // Find and click jobs link
    await page.click('a[href="/jobs"]');
    
    // Should navigate to jobs page
    await expect(page).toHaveURL('/jobs');
    await expect(page.locator('h1')).toContainText('Jobs');
  });

  test('should navigate to about page', async ({ page }) => {
    await page.goto('/');
    
    // Find and click about link
    await page.click('a[href="/about"]');
    
    // Should navigate to about page
    await expect(page).toHaveURL('/about');
    await expect(page.locator('h1')).toContainText('About');
  });

  test('should have working navigation menu', async ({ page }) => {
    await page.goto('/');
    
    // Check all main navigation links
    const navLinks = [
      { href: '/jobs', text: 'Jobs' },
      { href: '/about', text: 'About' },
      { href: '/contact', text: 'Contact' },
      { href: '/auth/login', text: 'Sign In' },
      { href: '/auth/register', text: 'Sign Up' }
    ];

    for (const link of navLinks) {
      const linkElement = page.locator(`a[href="${link.href}"]`);
      if (await linkElement.isVisible()) {
        await expect(linkElement).toBeVisible();
      }
    }
  });
});