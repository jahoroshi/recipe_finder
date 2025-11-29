import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import Pagination from '@/components/Pagination';

describe('Pagination Component', () => {
  const mockOnPageChange = vi.fn();

  afterEach(() => {
    mockOnPageChange.mockClear();
  });

  it('should render pagination with correct item count', () => {
    render(
      <Pagination
        currentPage={1}
        totalPages={5}
        totalItems={100}
        pageSize={20}
        onPageChange={mockOnPageChange}
      />
    );

    expect(screen.getByText((content, element) => {
      return element?.textContent === 'Showing 1 to 20 of 100 recipes';
    })).toBeInTheDocument();
  });

  it('should disable Previous button on first page', () => {
    render(
      <Pagination
        currentPage={1}
        totalPages={5}
        totalItems={100}
        pageSize={20}
        onPageChange={mockOnPageChange}
      />
    );

    const prevButton = screen.getByLabelText('Previous page');
    expect(prevButton).toBeDisabled();
  });

  it('should disable Next button on last page', () => {
    render(
      <Pagination
        currentPage={5}
        totalPages={5}
        totalItems={100}
        pageSize={20}
        onPageChange={mockOnPageChange}
      />
    );

    const nextButton = screen.getByLabelText('Next page');
    expect(nextButton).toBeDisabled();
  });

  it('should call onPageChange when clicking Next button', () => {
    render(
      <Pagination
        currentPage={2}
        totalPages={5}
        totalItems={100}
        pageSize={20}
        onPageChange={mockOnPageChange}
      />
    );

    const nextButton = screen.getByLabelText('Next page');
    fireEvent.click(nextButton);

    expect(mockOnPageChange).toHaveBeenCalledWith(3);
  });

  it('should call onPageChange when clicking Previous button', () => {
    render(
      <Pagination
        currentPage={3}
        totalPages={5}
        totalItems={100}
        pageSize={20}
        onPageChange={mockOnPageChange}
      />
    );

    const prevButton = screen.getByLabelText('Previous page');
    fireEvent.click(prevButton);

    expect(mockOnPageChange).toHaveBeenCalledWith(2);
  });

  it('should call onPageChange when clicking page number', () => {
    render(
      <Pagination
        currentPage={1}
        totalPages={5}
        totalItems={100}
        pageSize={20}
        onPageChange={mockOnPageChange}
      />
    );

    const page3Button = screen.getByLabelText('Go to page 3');
    fireEvent.click(page3Button);

    expect(mockOnPageChange).toHaveBeenCalledWith(3);
  });

  it('should highlight current page', () => {
    render(
      <Pagination
        currentPage={3}
        totalPages={5}
        totalItems={100}
        pageSize={20}
        onPageChange={mockOnPageChange}
      />
    );

    const currentPageButton = screen.getByLabelText('Go to page 3');
    expect(currentPageButton).toHaveClass('bg-teal-500');
  });

  it('should show ellipsis for large page counts', () => {
    render(
      <Pagination
        currentPage={5}
        totalPages={20}
        totalItems={400}
        pageSize={20}
        onPageChange={mockOnPageChange}
      />
    );

    const ellipses = screen.getAllByText('...');
    expect(ellipses.length).toBeGreaterThan(0);
  });

  it('should calculate correct item range for middle pages', () => {
    render(
      <Pagination
        currentPage={3}
        totalPages={5}
        totalItems={100}
        pageSize={20}
        onPageChange={mockOnPageChange}
      />
    );

    expect(screen.getByText((content, element) => {
      return element?.textContent === 'Showing 41 to 60 of 100 recipes';
    })).toBeInTheDocument();
  });

  it('should calculate correct item range for last page', () => {
    render(
      <Pagination
        currentPage={5}
        totalPages={5}
        totalItems={95}
        pageSize={20}
        onPageChange={mockOnPageChange}
      />
    );

    expect(screen.getByText((content, element) => {
      return element?.textContent === 'Showing 81 to 95 of 95 recipes';
    })).toBeInTheDocument();
  });

  it('should not render when only one page', () => {
    const { container } = render(
      <Pagination
        currentPage={1}
        totalPages={1}
        totalItems={10}
        pageSize={20}
        onPageChange={mockOnPageChange}
      />
    );

    expect(container.firstChild).toBeNull();
  });

  it('should render all pages when total pages <= 7', () => {
    render(
      <Pagination
        currentPage={3}
        totalPages={5}
        totalItems={100}
        pageSize={20}
        onPageChange={mockOnPageChange}
      />
    );

    expect(screen.getByLabelText('Go to page 1')).toBeInTheDocument();
    expect(screen.getByLabelText('Go to page 2')).toBeInTheDocument();
    expect(screen.getByLabelText('Go to page 3')).toBeInTheDocument();
    expect(screen.getByLabelText('Go to page 4')).toBeInTheDocument();
    expect(screen.getByLabelText('Go to page 5')).toBeInTheDocument();
  });
});
