"use client";

import { Card, CardContent } from "@/components/ui/card";

interface LoadingStateProps {
  count?: number;
}

export function LoadingState({ count = 6 }: LoadingStateProps) {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      {Array.from({ length: count }).map((_, i) => (
        <Card key={i} className="overflow-hidden">
          <div className="w-full h-48 skeleton" />
          <CardContent className="p-4 space-y-3">
            <div className="h-4 w-16 skeleton rounded" />
            <div className="space-y-2">
              <div className="h-5 skeleton rounded" />
              <div className="h-5 w-3/4 skeleton rounded" />
            </div>
            <div className="space-y-2">
              <div className="h-4 skeleton rounded" />
              <div className="h-4 w-5/6 skeleton rounded" />
            </div>
            <div className="flex justify-between">
              <div className="h-3 w-24 skeleton rounded" />
              <div className="h-3 w-16 skeleton rounded" />
            </div>
          </CardContent>
        </Card>
      ))}
    </div>
  );
}
