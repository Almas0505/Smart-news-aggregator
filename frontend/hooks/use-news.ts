"use client";

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { newsApi, userApi } from "@/lib/api";
import type { Article, PaginatedResponse, SearchParams } from "@/types";
import toast from "react-hot-toast";

// Get paginated news
export function useNews(params?: {
  page?: number;
  limit?: number;
  category?: string;
  source?: string;
}) {
  return useQuery({
    queryKey: ["news", params],
    queryFn: async () => {
      const response = await newsApi.getNews(params);
      return response.data as PaginatedResponse<Article>;
    },
  });
}

// Get single article
export function useArticle(id: string) {
  return useQuery({
    queryKey: ["article", id],
    queryFn: async () => {
      const response = await newsApi.getNewsById(id);
      return response.data as Article;
    },
    enabled: !!id,
  });
}

// Get trending news
export function useTrendingNews() {
  return useQuery({
    queryKey: ["trending"],
    queryFn: async () => {
      const response = await newsApi.getTrending();
      return response.data as Article[];
    },
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
}

// Get recommended news
export function useRecommendedNews() {
  return useQuery({
    queryKey: ["recommended"],
    queryFn: async () => {
      const response = await newsApi.getRecommended();
      return response.data as Article[];
    },
    staleTime: 10 * 60 * 1000, // 10 minutes
  });
}

// Search news
export function useSearchNews(params: SearchParams) {
  return useQuery({
    queryKey: ["search", params],
    queryFn: async () => {
      const response = await newsApi.searchNews(params.query, params);
      return response.data as PaginatedResponse<Article>;
    },
    enabled: !!params.query,
  });
}

// Bookmarks
export function useBookmarks() {
  return useQuery({
    queryKey: ["bookmarks"],
    queryFn: async () => {
      const response = await userApi.getBookmarks();
      return response.data as Article[];
    },
  });
}

export function useAddBookmark() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (newsId: string) => {
      const response = await userApi.addBookmark(newsId);
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["bookmarks"] });
      toast.success("Added to bookmarks");
    },
    onError: () => {
      toast.error("Failed to add bookmark");
    },
  });
}

export function useRemoveBookmark() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (newsId: string) => {
      const response = await userApi.removeBookmark(newsId);
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["bookmarks"] });
      toast.success("Removed from bookmarks");
    },
    onError: () => {
      toast.error("Failed to remove bookmark");
    },
  });
}

// Reading history
export function useReadingHistory() {
  return useQuery({
    queryKey: ["history"],
    queryFn: async () => {
      const response = await userApi.getHistory();
      return response.data as Article[];
    },
  });
}
