# 🎨 Smart News Aggregator - Frontend

Modern, responsive, and beautiful frontend for Smart News Aggregator built with Next.js 14.

## ✨ Features

- 🎨 **Modern UI** - Beautiful design with Tailwind CSS
- 🌗 **Dark Mode** - Seamless dark/light theme switching
- 📱 **Responsive** - Mobile-first design
- ⚡ **Fast** - Next.js 14 App Router with SSR
- 🔍 **Search** - Powerful search functionality
- 📊 **Categories** - Browse by topic
- 🤖 **AI-Powered** - Personalized recommendations
- 💾 **Bookmarks** - Save articles for later
- 📈 **Trending** - See what's hot
- 🎯 **Filters** - Filter by source, sentiment, date

## 🚀 Tech Stack

- **Framework:** Next.js 14
- **Language:** TypeScript
- **Styling:** Tailwind CSS
- **UI Components:** Custom + shadcn/ui style
- **State Management:** Zustand + React Query
- **Forms:** React Hook Form + Zod
- **Icons:** Lucide React
- **Animations:** Framer Motion

## 📦 Installation

```bash
# Install dependencies
npm install

# Copy environment variables
cp .env.local.example .env.local

# Edit .env.local with your API URL
# NEXT_PUBLIC_API_URL=http://localhost:8000

# Run development server
npm run dev

# Build for production
npm run build

# Start production server
npm start
```

## 🗂️ Project Structure

```
frontend/
├── app/                      # Next.js 14 app directory
│   ├── page.tsx             # Home page
│   ├── latest/              # Latest news page
│   ├── categories/          # Categories pages
│   ├── article/[id]/        # Article detail page
│   ├── layout.tsx           # Root layout
│   └── globals.css          # Global styles
│
├── components/
│   ├── layout/              # Layout components
│   │   ├── header.tsx
│   │   └── footer.tsx
│   ├── news/                # News components
│   │   ├── news-card.tsx
│   │   ├── news-list.tsx
│   │   ├── category-badge.tsx
│   │   ├── loading-state.tsx
│   │   └── empty-state.tsx
│   ├── ui/                  # UI components
│   │   ├── button.tsx
│   │   ├── card.tsx
│   │   └── badge.tsx
│   └── providers.tsx        # React Query + Theme providers
│
├── hooks/                   # Custom React hooks
│   ├── use-news.ts
│   └── use-categories.ts
│
├── lib/                     # Utilities
│   ├── api.ts              # API client
│   └── utils.ts            # Helper functions
│
└── types/                   # TypeScript types
    └── index.ts
```

## 🎯 Key Components

### NewsCard
Beautiful news card with multiple variants:
- **default** - Standard card with image
- **compact** - Small card for sidebars
- **featured** - Large hero card

```tsx
<NewsCard 
  article={article} 
  variant="featured"
  showImage={true}
  showCategory={true}
/>
```

### NewsList
Grid or list view of news articles:

```tsx
<NewsList 
  articles={articles}
  variant="grid"
  isLoading={false}
/>
```

### CategoryBadge
Colored category badges:

```tsx
<CategoryBadge 
  category={category}
  size="lg"
  clickable={true}
/>
```

## 🔌 API Integration

The frontend connects to the Backend API at `NEXT_PUBLIC_API_URL`.

### Available Hooks

```tsx
// Get news
const { data, isLoading } = useNews({ page: 1, limit: 12 });

// Get single article
const { data: article } = useArticle(id);

// Get trending
const { data: trending } = useTrendingNews();

// Get recommendations
const { data: recommended } = useRecommendedNews();

// Search
const { data: results } = useSearchNews({ query: "technology" });

// Categories
const { data: categories } = useCategories();

// Bookmarks
const { data: bookmarks } = useBookmarks();
const addBookmark = useAddBookmark();
const removeBookmark = useRemoveBookmark();
```

## 🎨 Styling

### Tailwind CSS

Custom theme with CSS variables for easy customization:

```css
:root {
  --primary: 221.2 83.2% 53.3%;
  --background: 0 0% 100%;
  /* ... more variables */
}

.dark {
  --primary: 217.2 91.2% 59.8%;
  --background: 222.2 84% 4.9%;
  /* ... more variables */
}
```

### Dark Mode

Toggle theme with useTheme hook:

```tsx
import { useTheme } from "next-themes";

const { theme, setTheme } = useTheme();
```

## 📱 Pages

### Home (`/`)
- Featured article
- Trending news
- Latest articles
- Category browser
- CTA section

### Latest (`/latest`)
- Paginated news list
- Filters

### Categories (`/categories`)
- Category grid
- Browse by topic

### Article Detail (`/article/[id]`)
- Full article content
- Related articles
- Tags and entities
- Social sharing
- Bookmarking

## 🛠️ Development

### Hot Reload
```bash
npm run dev
```

### Type Checking
```bash
npm run type-check
```

### Linting
```bash
npm run lint
```

### Build
```bash
npm run build
npm start
```

## 🚀 Deployment

### Vercel (Recommended)
```bash
vercel --prod
```

### Docker
```bash
docker build -t smart-news-frontend .
docker run -p 3000:3000 smart-news-frontend
```

### Environment Variables
```env
NEXT_PUBLIC_API_URL=https://api.smartnews.com
NEXT_PUBLIC_APP_NAME=Smart News Aggregator
NEXT_PUBLIC_APP_URL=https://smartnews.com
```

## 🎭 Features Showcase

### ✅ Implemented
- [x] Home page with featured articles
- [x] Latest news with pagination
- [x] Categories browser
- [x] Article detail page
- [x] Dark mode toggle
- [x] Responsive design
- [x] Loading states
- [x] Empty states
- [x] News cards (3 variants)
- [x] Category badges
- [x] API integration
- [x] React Query caching
- [x] Toast notifications

### 🚧 Coming Soon
- [ ] User authentication
- [ ] User profile page
- [ ] Personalized feed
- [ ] Advanced search
- [ ] Filter panel
- [ ] Reading history
- [ ] Comments system
- [ ] Social sharing
- [ ] PWA support
- [ ] Email notifications

## 📄 License

MIT License

---

**Built with ❤️ using Next.js 14**
