"use client";
import React from "react";
import { usePathname } from "next/navigation";
import Link from "next/link";
import { useAppStore } from "store";

interface IProps {
  isMobileView?: boolean;
}

const routes = [
  {
    name: "Datasets",
    url: "/settings/datasets",
    isAdmin: true,
  },
];

const SettingsLeftBar = ({ isMobileView = false }: IProps) => {
  const setIsSidebarOpen = useAppStore((state) => state.setIsSidebarOpen);
  const pathname = usePathname();
  const closeSidebar = () => {
    setIsSidebarOpen(false);
  };
  return (
    <div
      className={`${
        isMobileView ? "w-full" : "w-[370px]"
      } bg-white dark:bg-[#111111] transition-all h-full flex flex-col font-montserrat border-r-[#333333] relative`}
    >
      <div
        className={`${
          isMobileView
            ? "overflow-y-auto"
            : "overflow-y-hidden hover:overflow-y-auto"
        } flex-1 custom-scroll font-montserrat`}
      >
        <div className="p-5">
          <h2
            className={`font-semibold text-2xl dark:text-white mb-4 transition-all duration-1000`}
          >
            Settings
          </h2>
        </div>
        {routes?.map((route, index) => (
          <Link href={route.url} key={index}>
            <div
              onClick={() => closeSidebar()}
              key={index}
              className={`px-4 py-1 dark:text-white text-base truncate cursor-pointer hover:underline ${
                route.url === pathname ? "font-bold" : "font-light"
              }`}
            >
              {route.name}
            </div>
          </Link>
        ))}
      </div>
    </div>
  );
};

export default SettingsLeftBar;
