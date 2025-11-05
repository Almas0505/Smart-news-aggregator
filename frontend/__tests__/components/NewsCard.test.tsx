/**
 * Component Tests - News Card
 */

import { describe, it, expect, vi } from 'vitest'
import { render, screen } from '@testing-library/react'
import { NewsCard } from '@/components/news/news-card'

describe('NewsCard', () => {
  const mockArticle = {
    id: 1,
    title: 'Test Article Title',
    summary: 'This is a test summary',
    url: 'https://example.com/article',
    image_url: 'https://example.com/image.jpg',
    source: {
      id: 1,
      name: 'Test Source'
    },
    category: {
      id: 1,
      name: 'Technology'
    },
    published_at: new Date('2025-11-01').toISOString(),
    sentiment: 'positive',
    views_count: 100
  }

  it('renders article title', () => {
    render(<NewsCard article={mockArticle} />)
    expect(screen.getByText('Test Article Title')).toBeInTheDocument()
  })

  it('renders article summary', () => {
    render(<NewsCard article={mockArticle} />)
    expect(screen.getByText('This is a test summary')).toBeInTheDocument()
  })

  it('renders source name', () => {
    render(<NewsCard article={mockArticle} />)
    expect(screen.getByText('Test Source')).toBeInTheDocument()
  })

  it('renders category', () => {
    render(<NewsCard article={mockArticle} />)
    expect(screen.getByText('Technology')).toBeInTheDocument()
  })

  it('renders article without image', () => {
    const articleWithoutImage = { ...mockArticle, image_url: null }
    render(<NewsCard article={articleWithoutImage} />)
    expect(screen.getByText('Test Article Title')).toBeInTheDocument()
  })

  it('has correct link to article', () => {
    render(<NewsCard article={mockArticle} />)
    const link = screen.getByRole('link')
    expect(link).toHaveAttribute('href', expect.stringContaining('/article/1'))
  })
})
