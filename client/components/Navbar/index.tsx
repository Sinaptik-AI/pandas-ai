"use client";
import React from "react";
import { usePathname, useRouter } from "next/navigation";
import "react-modern-drawer/dist/index.css";
import LogoDark from "components/Icons/LogoDark";
import StartChatIcon from "components/Icons/StartChatIcon";
import SettingsMenu from "components/SettingsMenu";
import Link from "next/link";
import { ROUTE_CHAT_SCREEN } from "utils/constants";
import { BsGridFill, BsList } from "react-icons/bs";
import { useAppStore } from "store";

const Navbar = () => {
  const pathname = usePathname();
  const setIsSidebarOpen = useAppStore((state) => state.setIsSidebarOpen);
  const setIsNewChatClicked = useAppStore((state) => state.setIsNewChatClicked);
  const isSideBarOpen = useAppStore((state) => state.isSideBarOpen);
  const router = useRouter();

  return (
    <div className="w-full flex h-[75px] bg-black border-[#333333] border-b-[1px]">
      <div className="flex flex-grow w-[370px] items-center">
        <a href="#" onClick={() => setIsSidebarOpen(!isSideBarOpen)}>
          <BsList size={20} className="text-white ml-5 md:hidden" />
        </a>
        <Link href="/admin">
          <LogoDark width={70} height={70} />
        </Link>

        <div
          className="py-2 px-4 flex items-center bg-blue-700 rounded-md cursor-pointer text-[15px]"
          onClick={() => {
            router.push(ROUTE_CHAT_SCREEN);
            setIsNewChatClicked(true);
          }}
        >
          <StartChatIcon />
          <div className="text-white ml-2">New chat</div>
        </div>
      </div>
      <div className="flex w-[120px] justify-end">
        <SettingsMenu />
      </div>
    </div>
  );
};

export default Navbar;
