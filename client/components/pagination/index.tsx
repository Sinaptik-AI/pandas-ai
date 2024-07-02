import React from "react";
interface Pagination {
  page?: number;
  setPage?: React.Dispatch<React.SetStateAction<number>>;
  totalPages?: number;
}
const Pagination = ({ page, setPage, totalPages }: Pagination) => {
  const handlePrevious = () => {
    if (page > 1) {
      setPage(page - 1);
    }
  };

  const handleNext = () => {
    if (page < totalPages) {
      setPage(page + 1);
    }
  };

  if (totalPages <= 1) {
    return null;
  }

  const numPagesToShow = 5;

  const getPageNumbers = () => {
    const pageNumbers = [];
    const startPage = Math.max(1, page - Math.floor(numPagesToShow / 2));

    for (
      let i = startPage;
      i < Math.min(totalPages + 1, startPage + numPagesToShow);
      i++
    ) {
      pageNumbers.push(i);
    }

    return pageNumbers;
  };

  return (
    <>
      <nav>
        <ul className="inline-flex -space-x-px text-sm">
          <li>
            <a
              className={`dark:!bg-darkMain ml-0 flex h-8 items-center justify-center rounded-l-lg border border-[#333333] bg-white px-3 leading-tight text-[#31205f] dark:text-white cursor-pointer ${
                page === 1
                  ? "bg-blue-100 text-[#31205f] "
                  : "hover-bg-gray-200 hover-text-blue-700"
              } dark-border-gray-700 dark-bg-gray-800 dark-text-gray-400 ${
                page === 1
                  ? "dark-text-white"
                  : "dark-hover-bg-gray-700 dark-hover-text-white"
              }`}
              onClick={handlePrevious}
            >
              Previous
            </a>
          </li>
          {getPageNumbers().map((pageNumber) => (
            <li key={pageNumber}>
              <a
                className={`flex h-8 items-center justify-center border border-[#333333] bg-white px-3 leading-tight text-[#31205f] dark:text-white cursor-pointer ${
                  pageNumber === page
                    ? "dark-text-white active_page dark:!bg-[#333333]"
                    : "hover-bg-gray-20 dark:bg-darkMain"
                } dark-border-gray-700 dark-bg-gray-800 dark-text-gray-400`}
                onClick={() => setPage(pageNumber)}
              >
                {pageNumber}
              </a>
            </li>
          ))}
          <li>
            <a
              className={`dark:!bg-darkMain flex h-8 items-center justify-center rounded-r-lg border border-[#333333] bg-white px-3 leading-tight dark:text-white text-[#31205f] cursor-pointer  ${
                page === totalPages
                  ? "bg-blue-100 text-[#31205f]"
                  : "hover-bg-gray-200 hover-text-blue-700"
              } dark-border-gray-700 dark-bg-gray-800 dark-text-gray-400 ${
                page === totalPages
                  ? "dark-text-white"
                  : "dark-hover-bg-gray-700 dark-hover-text-white"
              }`}
              onClick={handleNext}
            >
              Next
            </a>
          </li>
        </ul>
      </nav>
    </>
  );
};

export default Pagination;
