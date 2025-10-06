"use client";

import { useQuery } from "@tanstack/react-query";
import { categoriesApi } from "@/lib/api";
import type { Category, Article, PaginatedResponse } from "@/types";

export function useCategories() {
  return useQuery({
    queryKey: ["categories"],
    queryFn: async () => {
      const response = await categoriesApi.getCategories();
      return response.data as Category[];
    },
    staleTime: 30 * 60 * 1000, // 30 minutes
  });
}

export function useCategoryNews(categoryId: string, page: number = 1) {
  return useQuery({
    queryKey: ["category-news", categoryId, page],
    queryFn: async () => {
      const response = await categoriesApi.getNewsByCategory(categoryId, {
        page,
      });
      return response.data as PaginatedResponse<Article>;
    },
    enabled: !!categoryId,
  });
}
