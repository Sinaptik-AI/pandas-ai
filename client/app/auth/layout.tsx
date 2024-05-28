"use client";
import { PropsWithChildren } from "react";

// Layout components
import React from "react";
import { isWindowAvailable } from "../../utils/navigation";

interface AuthProps extends PropsWithChildren {}

export default function AuthLayout({ children }: AuthProps) {
  // states and functions
  if (isWindowAvailable()) document.documentElement.dir = "ltr";
  return (
    <div>
      <div className="relative float-right h-full min-h-screen w-full dark:!bg-darkMain">
        <main className={`mx-auto min-h-screen`}>{children}</main>
      </div>
    </div>
  );
}
