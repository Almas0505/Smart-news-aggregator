"use client";

import { useState } from "react";
import { useNews } from "@/hooks/use-news";
import { NewsList } from "@/components/news/news-list";
import { Button } from "@/components/ui/button";
import { Clock, ChevronLeft, ChevronRight } from "lucide-react";

export default function LatestPage() {
  const [page, setPage] = useState(1);
  const { data, isLoading } = useNews({ page, limit: 12 });

  const handlePrevPage = () => {
    if (page > 1) {
      setPage(page - 1);
      window.scrollTo({ top: 0, behavior: "smooth" });
    }
  };

  const handleNextPage = () => {
    if (data && page < data.pages) {
      setPage(page + 1);
      window.scrollTo({ top: 0, behavior: "smooth" });
    }
  };

  return (
    <div className="container py-8 space-y-8">
      {/* Header */}
      <div>
        <h1 className="text-4xl font-bold tracking-tight mb-2 flex items-center gap-3">
          <Clock className="h-10 w-10 text-primary" />
          Latest News
        </h1>
        <p className="text-lg text-muted-foreground">
          Stay up to date with the most recent articles
        </p>
      </div>

      {/* News List */}
      <NewsList
        articles={data?.items || []}
        isLoading={isLoading}
        variant="grid"
      />

      {/* Pagination */}
      {data && data.pages > 1 && (
        <div className="flex items-center justify-center gap-4 py-8">
          <Button
            variant="outline"
            onClick={handlePrevPage}
            disabled={page === 1}
          >
            <ChevronLeft className="mr-2 h-4 w-4" />
            Previous
          </Button>

          <div className="flex items-center gap-2 text-sm">
            <span className="font-medium">
              Page {page} of {data.pages}
            </span>
            <span className="text-muted-foreground">
              ({data.total} articles)
            </span>
          </div>

          <Button
            variant="outline"
            onClick={handleNextPage}
            disabled={page >= data.pages}
          >
            Next
            <ChevronRight className="ml-2 h-4 w-4" />
          </Button>
        </div>
      )}
    </div>
  );
}
