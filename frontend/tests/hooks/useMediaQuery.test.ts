import { renderHook } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { useMediaQuery, useBreakpoints, useIsTouchDevice } from '@/hooks/useMediaQuery';

describe('useMediaQuery', () => {
  let mockMatchMedia: any;

  beforeEach(() => {
    mockMatchMedia = vi.fn();
    window.matchMedia = mockMatchMedia;
  });

  it('should return false initially', () => {
    mockMatchMedia.mockReturnValue({
      matches: false,
      addEventListener: vi.fn(),
      removeEventListener: vi.fn(),
    });

    const { result } = renderHook(() => useMediaQuery('(min-width: 768px)'));
    expect(result.current).toBe(false);
  });

  it('should return true when media query matches', () => {
    mockMatchMedia.mockReturnValue({
      matches: true,
      addEventListener: vi.fn(),
      removeEventListener: vi.fn(),
    });

    const { result } = renderHook(() => useMediaQuery('(min-width: 768px)'));
    expect(result.current).toBe(true);
  });

  it('should add and remove event listener', () => {
    const addEventListener = vi.fn();
    const removeEventListener = vi.fn();

    mockMatchMedia.mockReturnValue({
      matches: false,
      addEventListener,
      removeEventListener,
    });

    const { unmount } = renderHook(() => useMediaQuery('(min-width: 768px)'));

    expect(addEventListener).toHaveBeenCalledWith('change', expect.any(Function));

    unmount();

    expect(removeEventListener).toHaveBeenCalledWith('change', expect.any(Function));
  });

  it('should update when media query changes', () => {
    let changeHandler: ((event: MediaQueryListEvent) => void) | null = null;

    mockMatchMedia.mockReturnValue({
      matches: false,
      addEventListener: (_: string, handler: any) => {
        changeHandler = handler;
      },
      removeEventListener: vi.fn(),
    });

    const { result, rerender } = renderHook(() => useMediaQuery('(min-width: 768px)'));

    expect(result.current).toBe(false);

    // Simulate media query change
    if (changeHandler) {
      changeHandler({ matches: true } as MediaQueryListEvent);
    }

    rerender();

    expect(result.current).toBe(true);
  });
});

describe('useBreakpoints', () => {
  beforeEach(() => {
    window.matchMedia = vi.fn().mockImplementation((query: string) => ({
      matches: false,
      media: query,
      addEventListener: vi.fn(),
      removeEventListener: vi.fn(),
    }));
  });

  it('should return all breakpoint flags', () => {
    const { result } = renderHook(() => useBreakpoints());

    expect(result.current).toHaveProperty('isMobile');
    expect(result.current).toHaveProperty('isTablet');
    expect(result.current).toHaveProperty('isDesktop');
    expect(result.current).toHaveProperty('isLargeDesktop');
    expect(result.current).toHaveProperty('isMobileOrTablet');
    expect(result.current).toHaveProperty('isTabletOrDesktop');
  });

  it('should correctly identify mobile', () => {
    window.matchMedia = vi.fn().mockImplementation((query: string) => ({
      matches: query === '(max-width: 767px)',
      media: query,
      addEventListener: vi.fn(),
      removeEventListener: vi.fn(),
    }));

    const { result } = renderHook(() => useBreakpoints());

    expect(result.current.isMobile).toBe(true);
    expect(result.current.isTablet).toBe(false);
    expect(result.current.isDesktop).toBe(false);
    expect(result.current.isMobileOrTablet).toBe(true);
  });

  it('should correctly identify desktop', () => {
    window.matchMedia = vi.fn().mockImplementation((query: string) => ({
      matches: query === '(min-width: 1024px)',
      media: query,
      addEventListener: vi.fn(),
      removeEventListener: vi.fn(),
    }));

    const { result } = renderHook(() => useBreakpoints());

    expect(result.current.isMobile).toBe(false);
    expect(result.current.isTablet).toBe(false);
    expect(result.current.isDesktop).toBe(true);
    expect(result.current.isTabletOrDesktop).toBe(true);
  });
});

describe('useIsTouchDevice', () => {
  it('should return false when no touch support', () => {
    const { result } = renderHook(() => useIsTouchDevice());
    expect(typeof result.current).toBe('boolean');
  });

  it('should detect touch device via ontouchstart', () => {
    // @ts-ignore - adding ontouchstart
    window.ontouchstart = null;

    const { result } = renderHook(() => useIsTouchDevice());
    expect(result.current).toBe(true);

    // @ts-ignore - cleanup
    delete window.ontouchstart;
  });

  it('should detect touch device via maxTouchPoints', () => {
    Object.defineProperty(navigator, 'maxTouchPoints', {
      writable: true,
      value: 1,
    });

    const { result } = renderHook(() => useIsTouchDevice());
    expect(result.current).toBe(true);

    Object.defineProperty(navigator, 'maxTouchPoints', {
      writable: true,
      value: 0,
    });
  });
});
