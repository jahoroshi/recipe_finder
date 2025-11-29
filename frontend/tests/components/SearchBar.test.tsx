import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { render, screen, fireEvent, waitFor, act } from '@testing-library/react';
import SearchBar from '@/components/SearchBar';

describe('SearchBar', () => {
  it('renders with default placeholder', () => {
    const mockSetSearchQuery = vi.fn();
    render(
      <SearchBar searchQuery="" setSearchQuery={mockSetSearchQuery} />
    );

    const input = screen.getByRole('textbox');
    expect(input).toHaveAttribute('placeholder', 'Try: "quick vegetarian pasta under 30 minutes"');
  });

  it('renders with custom placeholder', () => {
    const mockSetSearchQuery = vi.fn();
    render(
      <SearchBar
        searchQuery=""
        setSearchQuery={mockSetSearchQuery}
        placeholder="Custom placeholder"
      />
    );

    const input = screen.getByRole('textbox');
    expect(input).toHaveAttribute('placeholder', 'Custom placeholder');
  });

  it('displays search query value', () => {
    const mockSetSearchQuery = vi.fn();
    render(
      <SearchBar searchQuery="test query" setSearchQuery={mockSetSearchQuery} />
    );

    const input = screen.getByRole('textbox') as HTMLInputElement;
    expect(input.value).toBe('test query');
  });

  it('calls setSearchQuery on input change', () => {
    const mockSetSearchQuery = vi.fn();
    render(
      <SearchBar searchQuery="" setSearchQuery={mockSetSearchQuery} />
    );

    const input = screen.getByRole('textbox');
    fireEvent.change(input, { target: { value: 'new query' } });

    expect(mockSetSearchQuery).toHaveBeenCalledWith('new query');
  });

  it('calls onSearch when Enter key is pressed', () => {
    const mockOnSearch = vi.fn();
    const mockSetSearchQuery = vi.fn();
    render(
      <SearchBar
        searchQuery="test"
        setSearchQuery={mockSetSearchQuery}
        onSearch={mockOnSearch}
      />
    );

    const input = screen.getByRole('textbox');
    fireEvent.keyPress(input, { key: 'Enter', code: 'Enter', charCode: 13 });

    expect(mockOnSearch).toHaveBeenCalledTimes(1);
  });

  it('calls onSearch when Search button is clicked', () => {
    const mockOnSearch = vi.fn();
    const mockSetSearchQuery = vi.fn();
    render(
      <SearchBar
        searchQuery="test"
        setSearchQuery={mockSetSearchQuery}
        onSearch={mockOnSearch}
      />
    );

    const button = screen.getByRole('button', { name: /^search$/i });
    fireEvent.click(button);

    expect(mockOnSearch).toHaveBeenCalledTimes(1);
  });

  it('disables search button when query is empty', () => {
    const mockOnSearch = vi.fn();
    const mockSetSearchQuery = vi.fn();
    render(
      <SearchBar
        searchQuery=""
        setSearchQuery={mockSetSearchQuery}
        onSearch={mockOnSearch}
      />
    );

    const button = screen.getByRole('button', { name: /^search$/i });
    expect(button).toBeDisabled();
  });

  it('disables search button when query is only whitespace', () => {
    const mockOnSearch = vi.fn();
    const mockSetSearchQuery = vi.fn();
    render(
      <SearchBar
        searchQuery="   "
        setSearchQuery={mockSetSearchQuery}
        onSearch={mockOnSearch}
      />
    );

    const button = screen.getByRole('button', { name: /^search$/i });
    expect(button).toBeDisabled();
  });

  it('shows loading state', () => {
    const mockSetSearchQuery = vi.fn();
    render(
      <SearchBar
        searchQuery="test"
        setSearchQuery={mockSetSearchQuery}
        onSearch={vi.fn()}
        isLoading={true}
      />
    );

    expect(screen.getByText(/searching/i)).toBeInTheDocument();
    expect(screen.getByRole('textbox')).toBeDisabled();
  });

  it('does not call onSearch when loading', () => {
    const mockOnSearch = vi.fn();
    const mockSetSearchQuery = vi.fn();
    render(
      <SearchBar
        searchQuery="test"
        setSearchQuery={mockSetSearchQuery}
        onSearch={mockOnSearch}
        isLoading={true}
      />
    );

    const input = screen.getByRole('textbox');
    fireEvent.keyPress(input, { key: 'Enter', code: 'Enter' });

    expect(mockOnSearch).not.toHaveBeenCalled();
  });

  it('shows clear button when query is present', () => {
    const mockSetSearchQuery = vi.fn();
    render(
      <SearchBar searchQuery="test" setSearchQuery={mockSetSearchQuery} showClear={true} />
    );

    const clearButton = screen.getByRole('button', { name: /clear search/i });
    expect(clearButton).toBeInTheDocument();
  });

  it('hides clear button when showClear is false', () => {
    const mockSetSearchQuery = vi.fn();
    render(
      <SearchBar searchQuery="test" setSearchQuery={mockSetSearchQuery} showClear={false} />
    );

    const clearButton = screen.queryByRole('button', { name: /clear search/i });
    expect(clearButton).not.toBeInTheDocument();
  });

  it('clears query when clear button is clicked', () => {
    const mockSetSearchQuery = vi.fn();
    render(
      <SearchBar searchQuery="test" setSearchQuery={mockSetSearchQuery} showClear={true} />
    );

    const clearButton = screen.getByRole('button', { name: /clear search/i });
    fireEvent.click(clearButton);

    expect(mockSetSearchQuery).toHaveBeenCalledWith('');
  });

  it('respects maxLength prop', () => {
    const mockSetSearchQuery = vi.fn();
    render(
      <SearchBar searchQuery="" setSearchQuery={mockSetSearchQuery} maxLength={100} />
    );

    const input = screen.getByRole('textbox');
    expect(input).toHaveAttribute('maxLength', '100');
  });

  it('auto-focuses when autoFocus is true', async () => {
    const mockSetSearchQuery = vi.fn();
    render(
      <SearchBar searchQuery="" setSearchQuery={mockSetSearchQuery} autoFocus={true} />
    );

    await waitFor(() => {
      const input = screen.getByRole('textbox');
      expect(input).toHaveFocus();
    });
  });
});

describe('SearchBar - Debouncing and Auto-search', () => {
  beforeEach(() => {
    vi.useFakeTimers();
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  it('should trigger auto-search after debounce delay when enabled', () => {
    const mockOnSearch = vi.fn();
    const mockSetSearchQuery = vi.fn();

    const { rerender } = render(
      <SearchBar
        searchQuery=""
        setSearchQuery={mockSetSearchQuery}
        onSearch={mockOnSearch}
        enableAutoSearch={true}
        debounceMs={500}
      />
    );

    // Update search query
    rerender(
      <SearchBar
        searchQuery="pasta"
        setSearchQuery={mockSetSearchQuery}
        onSearch={mockOnSearch}
        enableAutoSearch={true}
        debounceMs={500}
      />
    );

    // Should not be called immediately
    expect(mockOnSearch).not.toHaveBeenCalled();

    // Fast-forward time by 500ms
    act(() => {
      vi.advanceTimersByTime(500);
    });

    // Should be called after debounce
    expect(mockOnSearch).toHaveBeenCalledTimes(1);
  });

  it('should not trigger auto-search when enableAutoSearch is false', () => {
    const mockOnSearch = vi.fn();
    const mockSetSearchQuery = vi.fn();

    const { rerender } = render(
      <SearchBar
        searchQuery=""
        setSearchQuery={mockSetSearchQuery}
        onSearch={mockOnSearch}
        enableAutoSearch={false}
        debounceMs={500}
      />
    );

    rerender(
      <SearchBar
        searchQuery="pasta"
        setSearchQuery={mockSetSearchQuery}
        onSearch={mockOnSearch}
        enableAutoSearch={false}
        debounceMs={500}
      />
    );

    act(() => {
      vi.advanceTimersByTime(500);
    });

    expect(mockOnSearch).not.toHaveBeenCalled();
  });

  it('should cancel previous debounce on rapid changes', () => {
    const mockOnSearch = vi.fn();
    const mockSetSearchQuery = vi.fn();

    const { rerender } = render(
      <SearchBar
        searchQuery=""
        setSearchQuery={mockSetSearchQuery}
        onSearch={mockOnSearch}
        enableAutoSearch={true}
        debounceMs={500}
      />
    );

    // Rapid changes
    rerender(
      <SearchBar
        searchQuery="p"
        setSearchQuery={mockSetSearchQuery}
        onSearch={mockOnSearch}
        enableAutoSearch={true}
        debounceMs={500}
      />
    );
    act(() => {
      vi.advanceTimersByTime(100);
    });

    rerender(
      <SearchBar
        searchQuery="pa"
        setSearchQuery={mockSetSearchQuery}
        onSearch={mockOnSearch}
        enableAutoSearch={true}
        debounceMs={500}
      />
    );
    act(() => {
      vi.advanceTimersByTime(100);
    });

    rerender(
      <SearchBar
        searchQuery="pasta"
        setSearchQuery={mockSetSearchQuery}
        onSearch={mockOnSearch}
        enableAutoSearch={true}
        debounceMs={500}
      />
    );

    // Should not be called yet
    expect(mockOnSearch).not.toHaveBeenCalled();

    // Fast-forward by full debounce delay
    act(() => {
      vi.advanceTimersByTime(500);
    });

    // Should only be called once with the final value
    expect(mockOnSearch).toHaveBeenCalledTimes(1);
  });

  it('should use custom debounce delay', () => {
    const mockOnSearch = vi.fn();
    const mockSetSearchQuery = vi.fn();

    const { rerender } = render(
      <SearchBar
        searchQuery=""
        setSearchQuery={mockSetSearchQuery}
        onSearch={mockOnSearch}
        enableAutoSearch={true}
        debounceMs={1000}
      />
    );

    rerender(
      <SearchBar
        searchQuery="pizza"
        setSearchQuery={mockSetSearchQuery}
        onSearch={mockOnSearch}
        enableAutoSearch={true}
        debounceMs={1000}
      />
    );

    // Should not be called after 500ms
    act(() => {
      vi.advanceTimersByTime(500);
    });
    expect(mockOnSearch).not.toHaveBeenCalled();

    // Should be called after 1000ms
    act(() => {
      vi.advanceTimersByTime(500);
    });

    expect(mockOnSearch).toHaveBeenCalledTimes(1);
  });
});
