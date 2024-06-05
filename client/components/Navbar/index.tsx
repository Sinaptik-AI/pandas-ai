"use client";
import React from "react";
import "react-modern-drawer/dist/index.css";
import LogoDark from "components/Icons/LogoDark";
import SettingsMenu from "components/SettingsMenu";
import Link from "next/link";
import { BsList } from "react-icons/bs";
import { useAppStore } from "store";

const Navbar = () => {
  const setIsSidebarOpen = useAppStore((state) => state.setIsSidebarOpen);
  const isSideBarOpen = useAppStore((state) => state.isSideBarOpen);

  return (
    <div className="w-full flex h-[75px] bg-black border-[#333333] border-b-[1px]">
      <div className="flex flex-grow w-[370px] items-center">
        <a href="#" onClick={() => setIsSidebarOpen(!isSideBarOpen)}>
          <BsList size={20} className="text-white ml-5 md:hidden" />
        </a>
        <Link href="/admin">
          <LogoDark width={70} height={70} />
        </Link>
      </div>
      <div className="flex w-[120px] justify-end">
        <SettingsMenu />
      </div>
    </div>
  );
};

export default Navbar;
