"use client";

import { NewsCard } from "./news-card";
import { LoadingState } from "./loading-state";
import { EmptyState } from "./empty-state";
import type { Article } from "@/types";

interface NewsListProps {
  articles: Article[];
  isLoading?: boolean;
  variant?: "grid" | "list";
  cardVariant?: "default" | "compact" | "featured";
}

export function NewsList({
  articles,
  isLoading = false,
  variant = "grid",
  cardVariant = "default",
}: NewsListProps) {
  if (isLoading) {
    return <LoadingState count={variant === "grid" ? 6 : 5} />;
  }

  if (!articles || articles.length === 0) {
    return <EmptyState />;
  }

  if (variant === "list") {
    return (
      <div className="space-y-4">
        {articles.map((article) => (
          <NewsCard
            key={article.id}
            article={article}
            variant={cardVariant}
          />
        ))}
      </div>
    );
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      {articles.map((article) => (
        <NewsCard
          key={article.id}
          article={article}
          variant={cardVariant}
        />
      ))}
    </div>
  );
}
