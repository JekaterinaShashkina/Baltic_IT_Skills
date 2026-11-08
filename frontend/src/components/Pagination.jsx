export const Pagination = ({ pagination, onPageChange }) => {
  if (
    !pagination ||
    !Number.isInteger(pagination.page) ||
    !Number.isInteger(pagination.totalPages) ||
    pagination.totalPages <= 1
  ) {
    return null;
  }

  const { page, totalPages, total } = pagination;

  return (
    <nav className="pagination" aria-label="Job pages">
      <button
        type="button"
        disabled={page === 1}
        onClick={() => onPageChange(page - 1)}
      >
        ← Previous
      </button>

      <span>
        Page {page} of {totalPages} · {total} jobs
      </span>

      <button
        type="button"
        disabled={page === totalPages}
        onClick={() => onPageChange(page + 1)}
      >
        Next →
      </button>
    </nav>
  );
};
