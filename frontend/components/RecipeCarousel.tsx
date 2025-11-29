import React, { useRef, useState, useEffect } from 'react';
import type { SearchResult } from '@/types';
import SimilarRecipeCard from './SimilarRecipeCard';
import { useSwipe } from '@/hooks/useSwipe';
import { useBreakpoints } from '@/hooks/useMediaQuery';

interface RecipeCarouselProps {
  results: SearchResult[];
}

/**
 * Horizontal scrollable carousel for recipe cards
 * Features:
 * - Left/Right navigation arrows
 * - Touch swipe gestures (mobile)
 * - Smooth scrolling animation
 * - Keyboard support (arrow keys)
 * - Responsive card display
 * - Auto-hide arrows at boundaries
 */
const RecipeCarousel: React.FC<RecipeCarouselProps> = ({ results }) => {
  const scrollContainerRef = useRef<HTMLDivElement>(null);
  const [showLeftArrow, setShowLeftArrow] = useState(false);
  const [showRightArrow, setShowRightArrow] = useState(true);
  const { isMobile } = useBreakpoints();

  /**
   * Update arrow visibility based on scroll position
   */
  const updateArrowVisibility = () => {
    const container = scrollContainerRef.current;
    if (!container) return;

    const { scrollLeft, scrollWidth, clientWidth } = container;
    setShowLeftArrow(scrollLeft > 0);
    setShowRightArrow(scrollLeft < scrollWidth - clientWidth - 10); // 10px threshold
  };

  /**
   * Scroll to the left by one card width
   */
  const scrollLeft = () => {
    const container = scrollContainerRef.current;
    if (!container) return;

    const scrollAmount = 300; // Approximate card width + gap
    container.scrollBy({
      left: -scrollAmount,
      behavior: 'smooth',
    });
  };

  /**
   * Scroll to the right by one card width
   */
  const scrollRight = () => {
    const container = scrollContainerRef.current;
    if (!container) return;

    const scrollAmount = 300; // Approximate card width + gap
    container.scrollBy({
      left: scrollAmount,
      behavior: 'smooth',
    });
  };

  /**
   * Keyboard navigation support
   */
  const handleKeyDown = (e: KeyboardEvent) => {
    if (e.key === 'ArrowLeft') {
      e.preventDefault();
      scrollLeft();
    } else if (e.key === 'ArrowRight') {
      e.preventDefault();
      scrollRight();
    }
  };

  // Touch swipe gesture support
  const { ref: swipeRef } = useSwipe({
    onSwipeLeft: () => scrollRight(),
    onSwipeRight: () => scrollLeft(),
  }, {
    minSwipeDistance: 50,
    maxSwipeTime: 500,
  });

  // Merge refs
  useEffect(() => {
    if (scrollContainerRef.current && swipeRef.current === null) {
      // @ts-ignore - assigning the div to swipe ref
      swipeRef.current = scrollContainerRef.current;
    }
  }, [swipeRef]);

  // Set up scroll listener and keyboard support
  useEffect(() => {
    const container = scrollContainerRef.current;
    if (!container) return;

    // Initial arrow state
    updateArrowVisibility();

    // Listen to scroll events
    container.addEventListener('scroll', updateArrowVisibility);

    // Keyboard support
    window.addEventListener('keydown', handleKeyDown);

    return () => {
      container.removeEventListener('scroll', updateArrowVisibility);
      window.removeEventListener('keydown', handleKeyDown);
    };
  }, [results]);

  if (results.length === 0) {
    return null;
  }

  return (
    <div className="relative group">
      {/* Left Arrow - Hidden on mobile with touch support */}
      {showLeftArrow && !isMobile && (
        <button
          onClick={scrollLeft}
          className="absolute left-0 top-1/2 -translate-y-1/2 z-10 bg-white hover:bg-gray-100 text-gray-800 rounded-full p-3 shadow-lg transition-all duration-200 opacity-90 hover:opacity-100 focus:outline-none focus:ring-2 focus:ring-teal-500"
          aria-label="Scroll left"
        >
          <svg
            xmlns="http://www.w3.org/2000/svg"
            className="h-6 w-6"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M15 19l-7-7 7-7"
            />
          </svg>
        </button>
      )}

      {/* Carousel Container */}
      <div
        ref={scrollContainerRef}
        className="flex gap-4 overflow-x-auto scroll-smooth pb-4"
        style={{
          scrollbarWidth: 'none', // Firefox
          msOverflowStyle: 'none', // IE/Edge
        }}
      >
        {results.map((result) => (
          <SimilarRecipeCard key={result.recipe.id} result={result} />
        ))}
      </div>

      {/* Right Arrow - Hidden on mobile with touch support */}
      {showRightArrow && !isMobile && (
        <button
          onClick={scrollRight}
          className="absolute right-0 top-1/2 -translate-y-1/2 z-10 bg-white hover:bg-gray-100 text-gray-800 rounded-full p-3 shadow-lg transition-all duration-200 opacity-90 hover:opacity-100 focus:outline-none focus:ring-2 focus:ring-teal-500"
          aria-label="Scroll right"
        >
          <svg
            xmlns="http://www.w3.org/2000/svg"
            className="h-6 w-6"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M9 5l7 7-7 7"
            />
          </svg>
        </button>
      )}

      {/* Hide scrollbar */}
      <style>{`
        .overflow-x-auto::-webkit-scrollbar {
          display: none;
        }
      `}</style>
    </div>
  );
};

/**
 * Skeleton loader for carousel during loading state
 */
export const RecipeCarouselSkeleton: React.FC = () => {
  return (
    <div className="flex gap-4 overflow-hidden pb-4">
      {[1, 2, 3, 4].map((i) => (
        <div
          key={i}
          className="bg-white rounded-lg shadow-md overflow-hidden flex-shrink-0 animate-pulse"
          style={{ width: '280px' }}
        >
          {/* Image skeleton */}
          <div className="h-40 bg-gray-200" />
          {/* Content skeleton */}
          <div className="p-4">
            <div className="h-5 bg-gray-200 rounded w-3/4 mb-2" />
            <div className="h-4 bg-gray-200 rounded w-1/2 mb-3" />
            <div className="h-3 bg-gray-200 rounded w-full mb-2" />
            <div className="h-3 bg-gray-200 rounded w-5/6" />
          </div>
        </div>
      ))}
    </div>
  );
};

export default RecipeCarousel;
