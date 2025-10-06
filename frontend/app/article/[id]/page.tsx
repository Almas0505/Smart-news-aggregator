import Image from "next/image";
import Link from "next/link";
import { notFound } from "next/navigation";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import {
  Calendar,
  Clock,
  ExternalLink,
  Share2,
  Bookmark,
  ArrowLeft,
} from "lucide-react";
import { formatDate } from "@/lib/utils";
import { NewsCard } from "@/components/news/news-card";

async function getArticle(id: string) {
  try {
    const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
    const res = await fetch(`${API_URL}/api/v1/news/${id}`, {
      next: { revalidate: 300 },
    });
    if (!res.ok) return null;
    return await res.json();
  } catch {
    return null;
  }
}

async function getRelatedArticles(categoryId: string, currentId: string) {
  try {
    const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
    const res = await fetch(
      `${API_URL}/api/v1/categories/${categoryId}/news?limit=3`,
      { next: { revalidate: 300 } }
    );
    if (!res.ok) return [];
    const data = await res.json();
    return data.items.filter((a: any) => a.id !== currentId);
  } catch {
    return [];
  }
}

export default async function ArticlePage({
  params,
}: {
  params: { id: string };
}) {
  const article = await getArticle(params.id);

  if (!article) {
    notFound();
  }

  const relatedArticles = await getRelatedArticles(
    article.category.id,
    article.id
  );

  return (
    <div className="container py-8">
      <div className="max-w-4xl mx-auto">
        {/* Back Button */}
        <Button variant="ghost" size="sm" asChild className="mb-4">
          <Link href="/">
            <ArrowLeft className="mr-2 h-4 w-4" />
            Back to Home
          </Link>
        </Button>

        {/* Article Header */}
        <article className="space-y-6">
          {/* Category */}
          <Badge variant="secondary" className="text-sm">
            {article.category.name}
          </Badge>

          {/* Title */}
          <h1 className="text-4xl md:text-5xl font-bold tracking-tight">
            {article.title}
          </h1>

          {/* Summary */}
          <p className="text-xl text-muted-foreground leading-relaxed">
            {article.summary}
          </p>

          {/* Meta Info */}
          <div className="flex flex-wrap items-center gap-4 text-sm text-muted-foreground border-y py-4">
            <div className="flex items-center gap-2">
              <Calendar className="h-4 w-4" />
              <time>{formatDate(article.published_at)}</time>
            </div>
            {article.reading_time && (
              <div className="flex items-center gap-2">
                <Clock className="h-4 w-4" />
                <span>{article.reading_time} min read</span>
              </div>
            )}
            <div className="flex items-center gap-2 font-medium">
              <span>{article.source.name}</span>
            </div>
          </div>

          {/* Action Buttons */}
          <div className="flex gap-2">
            <Button variant="outline" size="sm">
              <Bookmark className="mr-2 h-4 w-4" />
              Save
            </Button>
            <Button variant="outline" size="sm">
              <Share2 className="mr-2 h-4 w-4" />
              Share
            </Button>
            <Button variant="outline" size="sm" asChild>
              <a href={article.url} target="_blank" rel="noopener noreferrer">
                <ExternalLink className="mr-2 h-4 w-4" />
                Read Original
              </a>
            </Button>
          </div>

          {/* Featured Image */}
          {article.image_url && (
            <div className="relative w-full h-96 rounded-lg overflow-hidden">
              <Image
                src={article.image_url}
                alt={article.title}
                fill
                className="object-cover"
                priority
              />
            </div>
          )}

          {/* Content */}
          <div className="prose prose-lg dark:prose-invert max-w-none">
            <div
              dangerouslySetInnerHTML={{
                __html: article.content
                  .replace(/\n/g, "<br />")
                  .replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>")
                  .replace(/\*(.*?)\*/g, "<em>$1</em>"),
              }}
            />
          </div>

          {/* Tags */}
          {article.tags && article.tags.length > 0 && (
            <div className="flex flex-wrap gap-2 pt-6 border-t">
              <span className="text-sm font-medium">Tags:</span>
              {article.tags.map((tag: any) => (
                <Badge key={tag.id} variant="outline">
                  {tag.name}
                </Badge>
              ))}
            </div>
          )}

          {/* Entities */}
          {article.entities && article.entities.length > 0 && (
            <Card>
              <CardContent className="p-6">
                <h3 className="font-semibold mb-3">Key Entities</h3>
                <div className="flex flex-wrap gap-2">
                  {article.entities.map((entity: any, i: number) => (
                    <Badge key={i} variant="secondary">
                      {entity.entity_text} ({entity.entity_type})
                    </Badge>
                  ))}
                </div>
              </CardContent>
            </Card>
          )}
        </article>

        {/* Related Articles */}
        {relatedArticles.length > 0 && (
          <section className="mt-16">
            <h2 className="text-2xl font-bold mb-6">Related Articles</h2>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              {relatedArticles.map((article: any) => (
                <NewsCard key={article.id} article={article} />
              ))}
            </div>
          </section>
        )}
      </div>
    </div>
  );
}
