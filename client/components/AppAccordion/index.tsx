import React from "react";
import { useAppStore } from "store";

interface IProps {
  title: string;
  children: React.ReactNode;
  islastItem?: boolean;
}

const AppAccordion = ({ title, children, islastItem = false }: IProps) => {
  const darkMode = useAppStore((state) => state.darkMode);

  return (
    <details
      className={`group dark:text-white ${islastItem ? " border-none" : " border-b border-[#333333]"}`}
      style={{ pointerEvents: "all" }}
    >
      <summary className="flex cursor-pointer list-none items-center gap-2   font-medium py-2">
        <span className="dark:text-white font-bold">{title}</span>
        <div className="wrapper_status_arrow flex">
          <span className="transition group-open:rotate-180">
            <svg
              fill="none"
              height="24"
              shapeRendering="geometricPrecision"
              stroke="currentColor"
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth="1.5"
              viewBox="0 0 24 24"
              width="24"
              color={darkMode ? "white" : "black"}
            >
              <path d="M6 9l6 6 6-6"></path>
            </svg>
          </span>
        </div>
      </summary>
      <div className="h-full p-2">{children}</div>
    </details>
  );
};

export default AppAccordion;
