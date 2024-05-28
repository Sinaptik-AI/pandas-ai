import { Loader } from "components/loader/Loader";
import React from "react";

interface IProps {
  disabled?: boolean;
  isLoading?: boolean;
  text: string;
  type?: "submit" | "reset" | "button";
  onClick?: () => void;
  className?: string;
}

const FormButton = ({
  disabled,
  isLoading,
  text,
  onClick,
  type = "button",
  className,
}: IProps) => {
  return (
    <button
      type={type}
      disabled={disabled}
      onClick={onClick}
      className={`px-8 py-1 border rounded-[10px] flex flex-wrap items-center justify-center cursor-pointer dark:bg-white neon-on-hover font-bold text-black font-montserrat ${className}`}
    >
      {isLoading ? <Loader heigth="h-6" width="w-10" /> : text}
    </button>
  );
};

export default FormButton;
