import { useEffect, useRef, useState } from 'react';

export interface SwipeHandlers {
  onSwipeLeft?: () => void;
  onSwipeRight?: () => void;
  onSwipeUp?: () => void;
  onSwipeDown?: () => void;
}

export interface SwipeConfig {
  minSwipeDistance?: number;
  maxSwipeTime?: number;
  preventDefaultTouchMove?: boolean;
}

export interface SwipeState {
  isSwiping: boolean;
  swipeDirection: 'left' | 'right' | 'up' | 'down' | null;
}

/**
 * Custom hook for detecting swipe gestures on touch devices
 *
 * @param handlers - Callback functions for different swipe directions
 * @param config - Configuration options for swipe detection
 * @returns Ref to attach to the element and swipe state
 *
 * @example
 * const { ref, isSwiping } = useSwipe({
 *   onSwipeLeft: () => console.log('Swiped left'),
 *   onSwipeRight: () => console.log('Swiped right'),
 * });
 *
 * return <div ref={ref}>Swipeable content</div>;
 */
export function useSwipe<T extends HTMLElement = HTMLDivElement>(
  handlers: SwipeHandlers,
  config: SwipeConfig = {}
) {
  const {
    minSwipeDistance = 50,
    maxSwipeTime = 500,
    preventDefaultTouchMove = false,
  } = config;

  const ref = useRef<T>(null);
  const [state, setState] = useState<SwipeState>({
    isSwiping: false,
    swipeDirection: null,
  });

  const touchStart = useRef<{ x: number; y: number; time: number } | null>(null);

  useEffect(() => {
    const element = ref.current;
    if (!element) return;

    const handleTouchStart = (e: TouchEvent) => {
      const touch = e.touches[0];
      touchStart.current = {
        x: touch.clientX,
        y: touch.clientY,
        time: Date.now(),
      };
      setState({ isSwiping: true, swipeDirection: null });
    };

    const handleTouchMove = (e: TouchEvent) => {
      if (preventDefaultTouchMove) {
        e.preventDefault();
      }
    };

    const handleTouchEnd = (e: TouchEvent) => {
      if (!touchStart.current) {
        setState({ isSwiping: false, swipeDirection: null });
        return;
      }

      const touch = e.changedTouches[0];
      const deltaX = touch.clientX - touchStart.current.x;
      const deltaY = touch.clientY - touchStart.current.y;
      const deltaTime = Date.now() - touchStart.current.time;

      // Reset touch start
      touchStart.current = null;

      // Check if swipe was fast enough
      if (deltaTime > maxSwipeTime) {
        setState({ isSwiping: false, swipeDirection: null });
        return;
      }

      const absX = Math.abs(deltaX);
      const absY = Math.abs(deltaY);

      // Determine swipe direction (horizontal vs vertical)
      if (absX > absY && absX > minSwipeDistance) {
        // Horizontal swipe
        const direction = deltaX > 0 ? 'right' : 'left';
        setState({ isSwiping: false, swipeDirection: direction });

        if (direction === 'left' && handlers.onSwipeLeft) {
          handlers.onSwipeLeft();
        } else if (direction === 'right' && handlers.onSwipeRight) {
          handlers.onSwipeRight();
        }
      } else if (absY > absX && absY > minSwipeDistance) {
        // Vertical swipe
        const direction = deltaY > 0 ? 'down' : 'up';
        setState({ isSwiping: false, swipeDirection: direction });

        if (direction === 'up' && handlers.onSwipeUp) {
          handlers.onSwipeUp();
        } else if (direction === 'down' && handlers.onSwipeDown) {
          handlers.onSwipeDown();
        }
      } else {
        setState({ isSwiping: false, swipeDirection: null });
      }
    };

    element.addEventListener('touchstart', handleTouchStart, { passive: true });
    element.addEventListener('touchmove', handleTouchMove, { passive: !preventDefaultTouchMove });
    element.addEventListener('touchend', handleTouchEnd, { passive: true });

    return () => {
      element.removeEventListener('touchstart', handleTouchStart);
      element.removeEventListener('touchmove', handleTouchMove);
      element.removeEventListener('touchend', handleTouchEnd);
    };
  }, [handlers, minSwipeDistance, maxSwipeTime, preventDefaultTouchMove]);

  return { ref, ...state };
}
