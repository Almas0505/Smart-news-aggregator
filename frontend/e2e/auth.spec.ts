/**
 * E2E Tests - User Authentication
 */

import { test, expect } from '@playwright/test';

test.describe('Authentication Flow', () => {
  test('should navigate to login page', async ({ page }) => {
    await page.goto('/');
    
    // Click login button
    const loginButton = page.getByRole('link', { name: /login/i });
    await loginButton.click();
    
    // Should be on login page
    await expect(page).toHaveURL(/\/login/);
    await expect(page.getByRole('heading', { name: /login/i })).toBeVisible();
  });

  test('should show validation errors on empty login form', async ({ page }) => {
    await page.goto('/login');
    
    // Try to submit empty form
    const submitButton = page.getByRole('button', { name: /login|sign in/i });
    await submitButton.click();
    
    // Should show validation errors
    await expect(page.getByText(/required|invalid/i).first()).toBeVisible();
  });

  test('should navigate to register page', async ({ page }) => {
    await page.goto('/');
    
    // Click register button
    const registerButton = page.getByRole('link', { name: /sign up|register/i });
    await registerButton.click();
    
    // Should be on register page
    await expect(page).toHaveURL(/\/register/);
  });

  test('should show validation errors on empty register form', async ({ page }) => {
    await page.goto('/register');
    
    // Try to submit empty form
    const submitButton = page.getByRole('button', { name: /register|sign up/i });
    await submitButton.click();
    
    // Should show validation errors
    await expect(page.getByText(/required/i).first()).toBeVisible();
  });

  test('should validate email format', async ({ page }) => {
    await page.goto('/login');
    
    // Enter invalid email
    const emailInput = page.getByLabel(/email/i);
    await emailInput.fill('invalid-email');
    
    const submitButton = page.getByRole('button', { name: /login|sign in/i });
    await submitButton.click();
    
    // Should show email validation error
    await expect(page.getByText(/invalid.*email/i)).toBeVisible();
  });
});

test.describe('Authenticated User Actions', () => {
  // This assumes you have a way to log in programmatically
  // Adjust based on your actual authentication implementation
  
  test.skip('should bookmark an article', async ({ page }) => {
    // Login first
    // await login(page, 'user@example.com', 'password');
    
    await page.goto('/');
    
    // Find bookmark button on first article
    const bookmarkButton = page.locator('[data-testid="bookmark-button"]').first();
    await bookmarkButton.click();
    
    // Should show success message
    await expect(page.getByText(/bookmarked|saved/i)).toBeVisible();
  });

  test.skip('should view bookmarked articles', async ({ page }) => {
    // Login first
    // await login(page, 'user@example.com', 'password');
    
    // Navigate to bookmarks page
    await page.goto('/bookmarks');
    
    // Should show bookmarked articles
    await expect(page.getByRole('heading', { name: /bookmarks/i })).toBeVisible();
  });
});
