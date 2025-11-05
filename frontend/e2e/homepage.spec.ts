/**
 * E2E Tests - Homepage
 */

import { test, expect } from '@playwright/test';

test.describe('Homepage', () => {
  test('should load homepage successfully', async ({ page }) => {
    await page.goto('/');
    
    // Check title
    await expect(page).toHaveTitle(/SmartNews/);
    
    // Check main heading
    await expect(page.getByRole('heading', { name: /Welcome to SmartNews/i })).toBeVisible();
  });

  test('should display categories', async ({ page }) => {
    await page.goto('/');
    
    // Wait for categories to load
    await page.waitForSelector('[data-testid="category-badge"]', { timeout: 5000 });
    
    // Check at least one category is displayed
    const categories = page.locator('[data-testid="category-badge"]');
    await expect(categories.first()).toBeVisible();
  });

  test('should display latest news', async ({ page }) => {
    await page.goto('/');
    
    // Wait for news cards to load
    await page.waitForSelector('[data-testid="news-card"]', { timeout: 5000 });
    
    // Check at least one news card is displayed
    const newsCards = page.locator('[data-testid="news-card"]');
    await expect(newsCards.first()).toBeVisible();
  });

  test('should navigate to article page when clicking on news card', async ({ page }) => {
    await page.goto('/');
    
    // Wait for news cards
    await page.waitForSelector('[data-testid="news-card"]');
    
    // Click first news card
    const firstCard = page.locator('[data-testid="news-card"]').first();
    await firstCard.click();
    
    // Should navigate to article page
    await expect(page).toHaveURL(/\/article\/\d+/);
  });

  test('should filter news by category', async ({ page }) => {
    await page.goto('/');
    
    // Wait for categories
    await page.waitForSelector('[data-testid="category-badge"]');
    
    // Click on first category
    const firstCategory = page.locator('[data-testid="category-badge"]').first();
    const categoryName = await firstCategory.textContent();
    await firstCategory.click();
    
    // Should navigate to category page
    await expect(page).toHaveURL(/\/categories\//);
    
    // Page should show category name
    if (categoryName) {
      await expect(page.getByText(categoryName)).toBeVisible();
    }
  });

  test('should have working search functionality', async ({ page }) => {
    await page.goto('/');
    
    // Find search input
    const searchInput = page.getByPlaceholder(/search/i);
    await searchInput.fill('artificial intelligence');
    
    // Submit search
    await searchInput.press('Enter');
    
    // Should show search results
    await expect(page).toHaveURL(/\/search/);
  });

  test('should toggle dark mode', async ({ page }) => {
    await page.goto('/');
    
    // Find theme toggle button
    const themeToggle = page.locator('[data-testid="theme-toggle"]');
    
    if (await themeToggle.count() > 0) {
      // Click theme toggle
      await themeToggle.click();
      
      // Check if dark mode class is added
      const html = page.locator('html');
      const classList = await html.getAttribute('class');
      expect(classList).toContain('dark');
    }
  });
});
