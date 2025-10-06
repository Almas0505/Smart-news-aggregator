// types/index.ts - Все типы приложения

export interface Article {
  id: string;
  title: string;
  content: string;
  summary: string;
  url: string;
  image_url?: string;
  source: Source;
  category: Category;
  sentiment: "positive" | "negative" | "neutral";
  published_at: string;
  scraped_at: string;
  created_at: string;
  tags?: Tag[];
  entities?: Entity[];
  reading_time?: number;
}

export interface Source {
  id: string;
  name: string;
  url: string;
  type: "rss" | "api" | "web";
  is_active: boolean;
}

export interface Category {
  id: string;
  name: string;
  slug: string;
  description?: string;
  icon?: string;
  color?: string;
}

export interface Tag {
  id: string;
  name: string;
}

export interface Entity {
  id: string;
  entity_type: "PERSON" | "ORG" | "LOCATION" | "PRODUCT";
  entity_text: string;
  confidence: number;
}

export interface User {
  id: string;
  email: string;
  full_name: string;
  avatar_url?: string;
  is_active: boolean;
  created_at: string;
  preferences?: UserPreferences;
}

export interface UserPreferences {
  categories: string[];
  sources: string[];
  notifications_enabled: boolean;
}

export interface Bookmark {
  id: string;
  user_id: string;
  news_id: string;
  created_at: string;
  article?: Article;
}

export interface ReadingHistory {
  id: string;
  user_id: string;
  news_id: string;
  read_at: string;
  read_duration?: number;
  article?: Article;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  size: number;
  pages: number;
}

export interface ApiError {
  detail: string;
  status: number;
}

export interface AuthTokens {
  access_token: string;
  refresh_token: string;
  token_type: string;
}

export interface LoginCredentials {
  email: string;
  password: string;
}

export interface RegisterData {
  email: string;
  password: string;
  full_name: string;
}

export interface SearchParams {
  query: string;
  category?: string;
  source?: string;
  sentiment?: "positive" | "negative" | "neutral";
  from_date?: string;
  to_date?: string;
  page?: number;
  limit?: number;
}

export interface FilterOptions {
  categories: Category[];
  sources: Source[];
  sentiments: Array<"positive" | "negative" | "neutral">;
  dateRange?: {
    from: string;
    to: string;
  };
}

// Component Props Types
export interface NewsCardProps {
  article: Article;
  variant?: "default" | "compact" | "featured";
  showImage?: boolean;
  showCategory?: boolean;
  showSource?: boolean;
  showSentiment?: boolean;
}

export interface NewsListProps {
  articles: Article[];
  isLoading?: boolean;
  variant?: "grid" | "list";
}

export interface CategoryBadgeProps {
  category: Category;
  size?: "sm" | "md" | "lg";
  clickable?: boolean;
}

export interface PaginationProps {
  currentPage: number;
  totalPages: number;
  onPageChange: (page: number) => void;
}

export interface FilterPanelProps {
  filters: FilterOptions;
  selectedFilters: Partial<SearchParams>;
  onFilterChange: (filters: Partial<SearchParams>) => void;
  onClearFilters: () => void;
}
