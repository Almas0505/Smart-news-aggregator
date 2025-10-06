"use client";

import Image from "next/image";
import Link from "next/link";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Bookmark, Share2, TrendingUp, Clock } from "lucide-react";
import { cn, formatDate } from "@/lib/utils";
import type { Article } from "@/types";
import { useAddBookmark, useRemoveBookmark } from "@/hooks/use-news";
import { useState } from "react";

interface NewsCardProps {
  article: Article;
  variant?: "default" | "compact" | "featured";
  showImage?: boolean;
  showCategory?: boolean;
  showSource?: boolean;
}

export function NewsCard({
  article,
  variant = "default",
  showImage = true,
  showCategory = true,
  showSource = true,
}: NewsCardProps) {
  const [isBookmarked, setIsBookmarked] = useState(false);
  const addBookmark = useAddBookmark();
  const removeBookmark = useRemoveBookmark();

  const handleBookmark = (e: React.MouseEvent) => {
    e.preventDefault();
    e.stopPropagation();

    if (isBookmarked) {
      removeBookmark.mutate(article.id);
    } else {
      addBookmark.mutate(article.id);
    }
    setIsBookmarked(!isBookmarked);
  };

  const handleShare = (e: React.MouseEvent) => {
    e.preventDefault();
    e.stopPropagation();
    
    if (navigator.share) {
      navigator.share({
        title: article.title,
        text: article.summary,
        url: `/article/${article.id}`,
      });
    }
  };

  // Sentiment colors
  const sentimentColors = {
    positive: "text-green-600 dark:text-green-400",
    negative: "text-red-600 dark:text-red-400",
    neutral: "text-gray-600 dark:text-gray-400",
  };

  if (variant === "compact") {
    return (
      <Link href={`/article/${article.id}`}>
        <Card className="overflow-hidden hover:shadow-md transition-shadow">
          <CardContent className="p-4">
            <div className="flex gap-3">
              {showImage && article.image_url && (
                <div className="relative w-20 h-20 flex-shrink-0 rounded overflow-hidden">
                  <Image
                    src={article.image_url}
                    alt={article.title}
                    fill
                    className="object-cover"
                  />
                </div>
              )}
              <div className="flex-1 min-w-0">
                <h3 className="font-semibold text-sm line-clamp-2 mb-1">
                  {article.title}
                </h3>
                <div className="flex items-center gap-2 text-xs text-muted-foreground">
                  {showSource && (
                    <span className="font-medium">{article.source.name}</span>
                  )}
                  <span>•</span>
                  <time>{formatDate(article.published_at)}</time>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      </Link>
    );
  }

  if (variant === "featured") {
    return (
      <Link href={`/article/${article.id}`}>
        <Card className="overflow-hidden hover:shadow-lg transition-all">
          {showImage && article.image_url && (
            <div className="relative w-full h-80">
              <Image
                src={article.image_url}
                alt={article.title}
                fill
                className="object-cover"
              />
              <div className="absolute inset-0 bg-gradient-to-t from-black/60 to-transparent" />
              <div className="absolute bottom-0 left-0 right-0 p-6 text-white">
                <h2 className="text-3xl font-bold mb-2 line-clamp-2">
                  {article.title}
                </h2>
                {showCategory && (
                  <Badge variant="secondary" className="mb-2">
                    {article.category.name}
                  </Badge>
                )}
              </div>
            </div>
          )}
          <CardContent className="p-6">
            <p className="text-muted-foreground mb-4 line-clamp-3">
              {article.summary}
            </p>
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3 text-sm text-muted-foreground">
                {showSource && (
                  <span className="font-medium">{article.source.name}</span>
                )}
                <span>•</span>
                <time>{formatDate(article.published_at)}</time>
                {article.reading_time && (
                  <>
                    <span>•</span>
                    <span className="flex items-center gap-1">
                      <Clock className="h-3 w-3" />
                      {article.reading_time} min
                    </span>
                  </>
                )}
              </div>
              <div className="flex gap-2">
                <Button
                  size="icon"
                  variant="ghost"
                  onClick={handleBookmark}
                  className={cn(isBookmarked && "text-primary")}
                >
                  <Bookmark
                    className="h-4 w-4"
                    fill={isBookmarked ? "currentColor" : "none"}
                  />
                </Button>
                <Button size="icon" variant="ghost" onClick={handleShare}>
                  <Share2 className="h-4 w-4" />
                </Button>
              </div>
            </div>
          </CardContent>
        </Card>
      </Link>
    );
  }

  // Default variant
  return (
    <Link href={`/article/${article.id}`}>
      <Card className="overflow-hidden hover:shadow-md transition-shadow group">
        {showImage && article.image_url && (
          <div className="relative w-full h-48 overflow-hidden">
            <Image
              src={article.image_url}
              alt={article.title}
              fill
              className="object-cover group-hover:scale-105 transition-transform duration-300"
            />
          </div>
        )}
        <CardContent className="p-4">
          {showCategory && (
            <Badge variant="secondary" className="mb-2">
              {article.category.name}
            </Badge>
          )}
          <h3 className="font-bold text-lg mb-2 line-clamp-2 group-hover:text-primary transition-colors">
            {article.title}
          </h3>
          <p className="text-sm text-muted-foreground mb-3 line-clamp-2">
            {article.summary}
          </p>
          <div className="flex items-center justify-between text-xs">
            <div className="flex items-center gap-2 text-muted-foreground">
              {showSource && (
                <span className="font-medium">{article.source.name}</span>
              )}
              <span>•</span>
              <time>{formatDate(article.published_at)}</time>
            </div>
            <div className="flex gap-1">
              <Button
                size="icon"
                variant="ghost"
                onClick={handleBookmark}
                className={cn(
                  "h-8 w-8",
                  isBookmarked && "text-primary"
                )}
              >
                <Bookmark
                  className="h-4 w-4"
                  fill={isBookmarked ? "currentColor" : "none"}
                />
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>
    </Link>
  );
}
