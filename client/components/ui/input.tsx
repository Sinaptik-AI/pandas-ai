import * as React from "react";

import { cn } from "@/lib/utils";

export interface InputProps
  extends React.InputHTMLAttributes<HTMLInputElement> {}

const Input = React.forwardRef<HTMLInputElement, InputProps>(
  ({ className, type, ...props }, ref) => {
    return (
      <input
        type={type}
        className={cn(
          "text-sm w-full text-dark dark:text-white dark:bg-[#333333] font-montserrat font-normal rounded-[25px] pl-4 focus:outline-none py-2 placeholder-darkMain dark:placeholder-white/30 shadow-md border border-gray-100 dark:border-none disabled:cursor-not-allowed disabled:opacity-50",
          className
        )}
        ref={ref}
        {...props}
      />
    );
  }
);
Input.displayName = "Input";

export { Input };
