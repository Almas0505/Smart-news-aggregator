import { NewsList } from "@/components/news/news-list";
import { NewsCard } from "@/components/news/news-card";
import { CategoryBadge } from "@/components/news/category-badge";
import { Button } from "@/components/ui/button";
import { TrendingUp, Zap, Clock } from "lucide-react";
import Link from "next/link";

// Server component - данные будут загружаться на сервере
async function getLatestNews() {
  try {
    const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
    const res = await fetch(`${API_URL}/api/v1/news?limit=9`, {
      next: { revalidate: 300 }, // Revalidate every 5 minutes
    });
    if (!res.ok) throw new Error("Failed to fetch");
    const data = await res.json();
    return data.items || [];
  } catch (error) {
    console.error("Error fetching news:", error);
    return [];
  }
}

async function getTrendingNews() {
  try {
    const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
    const res = await fetch(`${API_URL}/api/v1/news/trending`, {
      next: { revalidate: 600 }, // Revalidate every 10 minutes
    });
    if (!res.ok) throw new Error("Failed to fetch");
    return await res.json();
  } catch (error) {
    console.error("Error fetching trending:", error);
    return [];
  }
}

async function getCategories() {
  try {
    const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
    const res = await fetch(`${API_URL}/api/v1/categories`, {
      next: { revalidate: 1800 }, // Revalidate every 30 minutes
    });
    if (!res.ok) throw new Error("Failed to fetch");
    return await res.json();
  } catch (error) {
    console.error("Error fetching categories:", error);
    return [];
  }
}

export default async function HomePage() {
  const [latestNews, trendingNews, categories] = await Promise.all([
    getLatestNews(),
    getTrendingNews(),
    getCategories(),
  ]);

  const featuredArticle = latestNews[0];
  const regularArticles = latestNews.slice(1);

  return (
    <div className="container py-8 space-y-12">
      {/* Hero Section */}
      <section className="space-y-4">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-4xl font-bold tracking-tight mb-2">
              Welcome to <span className="text-primary">SmartNews</span>
            </h1>
            <p className="text-lg text-muted-foreground">
              Your AI-powered personalized news aggregator
            </p>
          </div>
          <Button asChild size="lg">
            <Link href="/for-you">
              <Zap className="mr-2 h-5 w-5" />
              For You
            </Link>
          </Button>
        </div>
      </section>

      {/* Categories */}
      <section>
        <h2 className="text-2xl font-bold mb-4 flex items-center gap-2">
          Browse Categories
        </h2>
        <div className="flex flex-wrap gap-2">
          {categories.slice(0, 8).map((category: any) => (
            <CategoryBadge key={category.id} category={category} size="lg" />
          ))}
        </div>
      </section>

      {/* Featured Article */}
      {featuredArticle && (
        <section>
          <h2 className="text-2xl font-bold mb-4 flex items-center gap-2">
            <TrendingUp className="h-6 w-6" />
            Featured Story
          </h2>
          <NewsCard article={featuredArticle} variant="featured" />
        </section>
      )}

      {/* Trending News - Sidebar */}
      {trendingNews.length > 0 && (
        <section>
          <h2 className="text-2xl font-bold mb-4 flex items-center gap-2">
            <TrendingUp className="h-6 w-6" />
            Trending Now
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            {trendingNews.slice(0, 4).map((article: any) => (
              <NewsCard
                key={article.id}
                article={article}
                variant="compact"
              />
            ))}
          </div>
        </section>
      )}

      {/* Latest News */}
      <section>
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-2xl font-bold flex items-center gap-2">
            <Clock className="h-6 w-6" />
            Latest News
          </h2>
          <Button variant="outline" asChild>
            <Link href="/latest">View All</Link>
          </Button>
        </div>
        <NewsList articles={regularArticles} variant="grid" />
      </section>

      {/* CTA Section */}
      <section className="bg-primary/5 rounded-lg p-8 text-center">
        <h2 className="text-2xl font-bold mb-2">
          Get Personalized News Recommendations
        </h2>
        <p className="text-muted-foreground mb-6">
          Sign up to get news tailored to your interests powered by AI
        </p>
        <div className="flex gap-4 justify-center">
          <Button size="lg" asChild>
            <Link href="/register">Sign Up Free</Link>
          </Button>
          <Button size="lg" variant="outline" asChild>
            <Link href="/login">Login</Link>
          </Button>
        </div>
      </section>
    </div>
  );
}
