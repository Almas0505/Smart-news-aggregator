/**
 * Component Tests - Category Badge
 */

import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import { CategoryBadge } from '@/components/news/category-badge'

describe('CategoryBadge', () => {
  const mockCategory = {
    id: 1,
    name: 'Technology',
    slug: 'technology'
  }

  it('renders category name', () => {
    render(<CategoryBadge category={mockCategory} />)
    expect(screen.getByText('Technology')).toBeInTheDocument()
  })

  it('is clickable and links to category page', () => {
    render(<CategoryBadge category={mockCategory} />)
    const link = screen.getByRole('link')
    expect(link).toHaveAttribute('href', expect.stringContaining('technology'))
  })

  it('renders with different sizes', () => {
    const { rerender } = render(<CategoryBadge category={mockCategory} size="sm" />)
    expect(screen.getByText('Technology')).toBeInTheDocument()
    
    rerender(<CategoryBadge category={mockCategory} size="lg" />)
    expect(screen.getByText('Technology')).toBeInTheDocument()
  })
})
