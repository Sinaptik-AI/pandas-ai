import * as React from "react";

import { cn } from "@/lib/utils";

export interface SelectProps
  extends React.SelectHTMLAttributes<HTMLSelectElement> {}

const Select = React.forwardRef<HTMLSelectElement, SelectProps>(
  ({ className, ...props }, ref) => {
    return (
      <div className="select-wrapper">
        <select
          className={cn(
            `text-sm w-full text-dark dark:text-white dark:bg-[#333333] font-montserrat font-normal rounded-[25px] p-4 
          focus:outline-none py-2 placeholder-darkMain dark:placeholder-white/30 shadow-md border cusselect dark:border-none 
          disabled:cursor-not-allowed disabled:opacity-50`,
            className
          )}
          ref={ref}
          {...props}
        >
          {props.children}
        </select>
      </div>
    );
  }
);
Select.displayName = "Select";

export interface OptionProps
  extends React.OptionHTMLAttributes<HTMLOptionElement> {}

const Option: React.FC<OptionProps> = ({ className, children, ...props }) => {
  return (
    <option
      className={cn(
        "text-dark dark:text-white dark:bg-[#333333] py-4",
        className
      )}
      {...props}
    >
      {children}
    </option>
  );
};

Option.displayName = "Option";

export { Select, Option };
