"use client";
import React, { useRef, useEffect, useState } from "react";
import { cn } from "@/lib/utils";
import ChatSearchIcon from "../Icons/ChatSearchIcon";

interface DataType {
  id: string | number;
  name: string;
}

export interface AutoCompleteProps
  extends React.InputHTMLAttributes<HTMLInputElement> {
  onItemClick: (item: DataType) => void;
  onSubmit: (e) => void;
  data: DataType[];
}

const AutoComplete = React.forwardRef<HTMLInputElement, AutoCompleteProps>(
  ({ className, onItemClick, onSubmit, data, ...props }, ref) => {
    const hoverRef = useRef(null);
    const [cursor, setCursor] = useState(0);
    const [options, setOptions] = useState([]);

    useEffect(() => {
      function handleClickOutside(event: MouseEvent) {
        if (
          hoverRef.current &&
          !hoverRef.current.contains(event.target as Node)
        ) {
          setOptions([]);
          setCursor(0);
        }
      }
      document.addEventListener("mousedown", handleClickOutside);
      return () => {
        document.removeEventListener("mousedown", handleClickOutside);
      };
    }, []);

    const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
      if (e.key === "ArrowUp" && cursor > 0) {
        setCursor(cursor - 1);
      } else if (
        e.key === "ArrowDown" &&
        cursor < options.slice(0, 5).length - 1
      ) {
        setCursor(cursor + 1);
      } else if (e.key === "Enter") {
        e.preventDefault();
        onItemClick(options[cursor]);
        setOptions([]);
        setCursor(0);
      }
    };

    const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
      const value = e.target.value.toLowerCase();
      const filteredOptions = data.filter((item) =>
        item.name.toLowerCase().includes(value)
      );
      setOptions(filteredOptions || []);
    };

    return (
      <div className="relative w-full">
        <form onSubmit={onSubmit}>
          <div className="relative">
            <input
              type="text"
              className={cn(
                `text-sm w-full text-dark dark:text-white dark:bg-[#333333] font-montserrat font-normal pl-4 
                focus:outline-none py-2 placeholder-darkMain dark:placeholder-white/30 shadow-md border border-gray-100 
                dark:border-none disabled:cursor-not-allowed disabled:opacity-50
                ${options.length > 0 ? "rounded-t-[18px]" : "rounded-[25px]"}
                `,
                className
              )}
              ref={ref}
              onKeyDown={handleKeyDown}
              onChange={handleChange}
              {...props}
            />
            <span className="absolute inset-y-0 right-0 flex items-center pr-4">
              <button
                type="submit"
                className="focus:outline-none focus:shadow-outline"
              >
                <ChatSearchIcon />
              </button>
            </span>
          </div>
        </form>
        {options.length > 0 && (
          <div
            id="options"
            ref={hoverRef}
            className="absolute w-full z-10 rounded-b-[18px] dark:bg-[#1f1f1f]"
          >
            {options?.slice(0, 5).map((item: DataType, index: number) => (
              <div
                className={`cursor-pointer px-4 py-2 w-full dark:text-white
              ${
                index === options.length - 1
                  ? "hover:dark:bg-blue-700 hover:bg-gray-200 hover:rounded-b-[18px]"
                  : "hover:dark:bg-blue-700 hover:bg-gray-200"
              }
              `}
                key={item.id}
                onClick={() => {
                  onItemClick(item);
                  setOptions([]);
                  setCursor(0);
                }}
              >
                <p className="dark:text-white font-montserrat">{item?.name}</p>
              </div>
            ))}
          </div>
        )}
      </div>
    );
  }
);
AutoComplete.displayName = "Input";

export { AutoComplete };
