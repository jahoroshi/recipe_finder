import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { renderHook, act, waitFor } from '@testing-library/react';
import { useDebounce, useDebouncedCallback } from '@/hooks/useDebounce';

describe('useDebounce', () => {
  beforeEach(() => {
    vi.useFakeTimers();
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  it('should return initial value immediately', () => {
    const { result } = renderHook(() => useDebounce('test', 500));
    expect(result.current).toBe('test');
  });

  it('should debounce value changes', () => {
    const { result, rerender } = renderHook(
      ({ value, delay }) => useDebounce(value, delay),
      {
        initialProps: { value: 'initial', delay: 500 },
      }
    );

    expect(result.current).toBe('initial');

    // Change value
    rerender({ value: 'updated', delay: 500 });

    // Should still be initial value immediately after change
    expect(result.current).toBe('initial');

    // Fast-forward time by 500ms
    act(() => {
      vi.advanceTimersByTime(500);
    });

    // Now should be updated
    expect(result.current).toBe('updated');
  });

  it('should cancel previous timeout on rapid changes', () => {
    const { result, rerender } = renderHook(
      ({ value }) => useDebounce(value, 500),
      {
        initialProps: { value: 'initial' },
      }
    );

    // Rapid changes
    rerender({ value: 'first' });
    act(() => {
      vi.advanceTimersByTime(100);
    });

    rerender({ value: 'second' });
    act(() => {
      vi.advanceTimersByTime(100);
    });

    rerender({ value: 'third' });

    // Only 200ms passed, still should be initial
    expect(result.current).toBe('initial');

    // Advance full 500ms from last change
    act(() => {
      vi.advanceTimersByTime(500);
    });

    // Should be the last value
    expect(result.current).toBe('third');
  });

  it('should use custom delay', () => {
    const { result, rerender } = renderHook(
      ({ value, delay }) => useDebounce(value, delay),
      {
        initialProps: { value: 'initial', delay: 1000 },
      }
    );

    rerender({ value: 'updated', delay: 1000 });

    // After 500ms, should still be initial
    act(() => {
      vi.advanceTimersByTime(500);
    });
    expect(result.current).toBe('initial');

    // After 1000ms total, should be updated
    act(() => {
      vi.advanceTimersByTime(500);
    });

    expect(result.current).toBe('updated');
  });

  it('should handle different data types', () => {
    // Test with number
    const { result: numberResult, rerender: rerenderNumber } = renderHook(
      ({ value }) => useDebounce(value, 500),
      { initialProps: { value: 0 } }
    );

    rerenderNumber({ value: 42 });
    act(() => {
      vi.advanceTimersByTime(500);
    });
    expect(numberResult.current).toBe(42);

    // Test with object
    const { result: objectResult, rerender: rerenderObject } = renderHook(
      ({ value }) => useDebounce(value, 500),
      { initialProps: { value: { test: 'initial' } } }
    );

    const newObject = { test: 'updated' };
    rerenderObject({ value: newObject });
    act(() => {
      vi.advanceTimersByTime(500);
    });
    expect(objectResult.current).toEqual(newObject);
  });

  it('should use default delay of 500ms when not specified', () => {
    const { result, rerender } = renderHook(
      ({ value }) => useDebounce(value),
      { initialProps: { value: 'initial' } }
    );

    rerender({ value: 'updated' });

    // Should still be initial after 400ms
    act(() => {
      vi.advanceTimersByTime(400);
    });
    expect(result.current).toBe('initial');

    // Should be updated after 500ms total
    act(() => {
      vi.advanceTimersByTime(100);
    });
    expect(result.current).toBe('updated');
  });
});

describe('useDebouncedCallback', () => {
  beforeEach(() => {
    vi.useFakeTimers();
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  it('should debounce callback execution', () => {
    const callback = vi.fn();
    const { result } = renderHook(() => useDebouncedCallback(callback, 500));

    // Call the debounced function
    act(() => {
      result.current('test');
    });

    // Callback should not be called immediately
    expect(callback).not.toHaveBeenCalled();

    // Fast-forward time
    act(() => {
      vi.advanceTimersByTime(500);
    });

    // Now callback should be called
    expect(callback).toHaveBeenCalledTimes(1);
    expect(callback).toHaveBeenCalledWith('test');
  });

  it('should cancel previous callback on rapid calls', () => {
    const callback = vi.fn();
    const { result } = renderHook(() => useDebouncedCallback(callback, 500));

    // Rapid calls
    act(() => {
      result.current('first');
      vi.advanceTimersByTime(100);
      result.current('second');
      vi.advanceTimersByTime(100);
      result.current('third');
    });

    // Advance to complete debounce
    act(() => {
      vi.advanceTimersByTime(500);
    });

    // Should only be called once with the last value
    expect(callback).toHaveBeenCalledTimes(1);
    expect(callback).toHaveBeenCalledWith('third');
  });

  it('should handle multiple arguments', () => {
    const callback = vi.fn();
    const { result } = renderHook(() => useDebouncedCallback(callback, 500));

    act(() => {
      result.current('arg1', 'arg2', 'arg3');
    });

    act(() => {
      vi.advanceTimersByTime(500);
    });

    expect(callback).toHaveBeenCalledWith('arg1', 'arg2', 'arg3');
  });

  it('should use custom delay', () => {
    const callback = vi.fn();
    const { result } = renderHook(() => useDebouncedCallback(callback, 1000));

    act(() => {
      result.current('test');
    });

    // After 500ms, should not be called
    act(() => {
      vi.advanceTimersByTime(500);
    });
    expect(callback).not.toHaveBeenCalled();

    // After 1000ms total, should be called
    act(() => {
      vi.advanceTimersByTime(500);
    });
    expect(callback).toHaveBeenCalledTimes(1);
  });

  it('should use default delay of 500ms when not specified', () => {
    const callback = vi.fn();
    const { result } = renderHook(() => useDebouncedCallback(callback));

    act(() => {
      result.current('test');
    });

    act(() => {
      vi.advanceTimersByTime(500);
    });

    expect(callback).toHaveBeenCalledTimes(1);
  });

  it('should preserve callback context', () => {
    const context = { value: 'test' };
    const callback = vi.fn(function (this: typeof context) {
      return this.value;
    });

    const { result } = renderHook(() => useDebouncedCallback(callback.bind(context), 500));

    act(() => {
      result.current();
    });

    act(() => {
      vi.advanceTimersByTime(500);
    });

    expect(callback).toHaveBeenCalled();
  });
});
