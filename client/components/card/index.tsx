import React from "react";

function Card(props: {
  className?: string;
  extra?: string;
  children?: React.ReactNode; // Simplified type
  default?: boolean;
}) {
  const { extra, children, ...rest } = props;
  return (
    <div
      className={`!z-5 relative flex flex-col rounded-[20px] shadow-[rgba(0, 0, 0, 0.2)] shadow-md border border-gray-100 dark:border-none dark:shadow-none bg-clip-border dark:!bg-darkMain dark:text-white  ${extra}`}
      {...rest}
    >
      {children} {/* Removed unnecessary fragment */}
    </div>
  );
}

export default Card;
