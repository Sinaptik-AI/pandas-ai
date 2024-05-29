import React from "react";

interface IProps {
  height?: string;
  width?: string;
}

export const Loader = ({ height = "h-96", width = "w-14" }: IProps) => {
  return (
    <div className="flex justify-center align-center">
      <svg
        className={`${height} ${width} animate-spin text-white`}
        xmlns="http://www.w3.org/2000/svg"
        fill="none"
        viewBox="0 0 24 24"
      >
        <circle cx="12" cy="12" r="10" stroke="orange" strokeWidth="4"></circle>
        <path
          className="opacity-75"
          fill="currentColor"
          d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
        ></path>
      </svg>
    </div>
  );
};
