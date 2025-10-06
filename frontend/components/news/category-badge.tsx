"use client";

import Link from "next/link";
import { Badge } from "@/components/ui/badge";
import { cn } from "@/lib/utils";
import type { Category } from "@/types";

interface CategoryBadgeProps {
  category: Category;
  size?: "sm" | "md" | "lg";
  clickable?: boolean;
}

const categoryColors: Record<string, string> = {
  technology: "bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200",
  business: "bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200",
  sports: "bg-orange-100 text-orange-800 dark:bg-orange-900 dark:text-orange-200",
  entertainment: "bg-purple-100 text-purple-800 dark:bg-purple-900 dark:text-purple-200",
  health: "bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200",
  science: "bg-cyan-100 text-cyan-800 dark:bg-cyan-900 dark:text-cyan-200",
  politics: "bg-gray-100 text-gray-800 dark:bg-gray-900 dark:text-gray-200",
};

export function CategoryBadge({
  category,
  size = "md",
  clickable = true,
}: CategoryBadgeProps) {
  const colorClass = categoryColors[category.slug] || categoryColors.politics;

  const sizeClass = {
    sm: "text-xs px-2 py-0.5",
    md: "text-sm px-2.5 py-0.5",
    lg: "text-base px-3 py-1",
  };

  const badge = (
    <Badge
      variant="secondary"
      className={cn(
        colorClass,
        sizeClass[size],
        clickable && "hover:opacity-80 cursor-pointer transition-opacity"
      )}
    >
      {category.name}
    </Badge>
  );

  if (clickable) {
    return (
      <Link href={`/categories/${category.slug}`}>
        {badge}
      </Link>
    );
  }

  return badge;
}
