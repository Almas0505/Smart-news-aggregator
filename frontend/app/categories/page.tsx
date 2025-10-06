"use client";

import Link from "next/link";
import { useCategories } from "@/hooks/use-categories";
import { Card, CardContent } from "@/components/ui/card";
import { CategoryBadge } from "@/components/news/category-badge";
import { LoadingState } from "@/components/news/loading-state";
import { Folder, ArrowRight } from "lucide-react";

export default function CategoriesPage() {
  const { data: categories, isLoading } = useCategories();

  if (isLoading) {
    return (
      <div className="container py-8">
        <LoadingState count={8} />
      </div>
    );
  }

  return (
    <div className="container py-8 space-y-8">
      {/* Header */}
      <div>
        <h1 className="text-4xl font-bold tracking-tight mb-2 flex items-center gap-3">
          <Folder className="h-10 w-10 text-primary" />
          Categories
        </h1>
        <p className="text-lg text-muted-foreground">
          Browse news by topic and interest
        </p>
      </div>

      {/* Categories Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {categories?.map((category) => (
          <Link
            key={category.id}
            href={`/categories/${category.slug}`}
            className="group"
          >
            <Card className="h-full hover:shadow-lg transition-shadow">
              <CardContent className="p-6">
                <div className="flex items-start justify-between mb-4">
                  <CategoryBadge
                    category={category}
                    size="lg"
                    clickable={false}
                  />
                  <ArrowRight className="h-5 w-5 text-muted-foreground group-hover:text-primary transition-colors" />
                </div>
                <h3 className="text-xl font-bold mb-2 group-hover:text-primary transition-colors">
                  {category.name}
                </h3>
                {category.description && (
                  <p className="text-sm text-muted-foreground line-clamp-2">
                    {category.description}
                  </p>
                )}
              </CardContent>
            </Card>
          </Link>
        ))}
      </div>
    </div>
  );
}
