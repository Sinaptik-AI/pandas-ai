import React from "react";
import Link from "next/link";

const Button = ({
  link,
  text,
  className,
}: {
  link?: string;
  text: string;
  className?: string;
}) => (
  <Link href={link || undefined}>
    <div
      className={`px-8 py-1 border rounded-[10px] flex flex-wrap items-center justify-center cursor-pointer dark:bg-white neon-on-hover ${className}`}
    >
      <span className="font-bold text-black font-montserrat">{text}</span>
    </div>
  </Link>
);
export default Button;
