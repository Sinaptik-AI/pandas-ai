"use client";
import LogoDark from "components/Icons/LogoDark";
import React, { useState } from "react";
import ToggleDarkModeComponent from "components/ToggleDarkMode";
import StartChatIcon from "components/Icons/StartChatIcon";
import { useRouter } from "next/navigation";
import { useAppStore } from "store";
import { ROUTE_CHAT_SCREEN } from "utils/constants";
import ConversationItem from "./ConversationItem";

interface IProps {
  isMobileView?: boolean;
}

const LeftBar = ({ isMobileView = false }: IProps) => {
  const setIsSidebarOpen = useAppStore((state) => state.setIsSidebarOpen);
  const isSidebarOpen = useAppStore((state) => state.isSideBarOpen);
  const router = useRouter();
  const [collapsed, setCollapsed] = useState(false);
  const darkMode = useAppStore((state) => state.darkMode);

  const closeSidebar = () => {
    setIsSidebarOpen(false);
  };

  return (
    <>
      {!isMobileView ? (
        <div
          className={`bg-white dark:bg-black h-full flex flex-col font-montserrat border-r-[#333333] relative transition-all overflow-hidden md:overflow-visible ${
            collapsed ? "md:w-[20px]" : "md:w-[370px]"
          } ${isSidebarOpen ? "w-[370px]" : "w-0"}`}
        >
          <div
            className={`absolute right-[-16px] top-[45vh] w-8 h-8 rounded-full bg-white dark:bg-[#111111] border border-[#333333] cursor-pointer z-50 hidden md:flex`}
            onClick={() => setCollapsed(!collapsed)}
          >
            <div className="w-5 h-5 mt-1">
              {collapsed ? (
                <svg
                  className="ml-[8px]"
                  width="100%"
                  height="100%"
                  viewBox="0 0 24 24"
                  fill="none"
                  xmlns="http://www.w3.org/2000/svg"
                >
                  <path
                    d="M6 18L14 12L6 6"
                    stroke={darkMode ? "#ffffff" : "#000000"}
                    strokeWidth="2"
                    strokeLinecap="round"
                    strokeLinejoin="round"
                  />
                </svg>
              ) : (
                <svg
                  className="ml-[4px]"
                  width="100%"
                  height="100%"
                  viewBox="0 0 24 24"
                  fill="none"
                  xmlns="http://www.w3.org/2000/svg"
                >
                  <path
                    d="M16 18L8 12L16 6"
                    stroke={darkMode ? "#ffffff" : "#000000"}
                    strokeWidth="2"
                    strokeLinecap="round"
                    strokeLinejoin="round"
                  />
                </svg>
              )}
            </div>
          </div>
          {/* Conversation */}

          <div
            className={`${
              isSidebarOpen
                ? "w-full overflow-y-auto"
                : "overflow-y-hidden hover:overflow-y-auto overflow-x-hidden"
            } p-5 h-full flex flex-col custom-scroll`}
          >
            <h2
              className={`font-semibold text-2xl ${
                collapsed ? "opacity-0 pointer-events-none" : "opacity-100"
              } dark:text-white mb-4 transition-all duration-1000`}
            >
              Chats
            </h2>
            <ConversationItem collapsed={collapsed} />
          </div>
        </div>
      ) : (
        <div
          className={`w-full h-full flex flex-col font-montserrat border-r-[#333333] relative bg-white dark:bg-black`}
        >
          <div
            className="w-[80px] m-2 cursor-pointer"
            onClick={() => {
              router.push("/admin");
              closeSidebar();
            }}
          >
            <LogoDark />
          </div>
          <div className="pt-2 pb-8 px-4 mt-3 flex flex-col gap-2 text-[15px] font-semibold font-montserrat">
            <div
              onClick={() => {
                router.push(ROUTE_CHAT_SCREEN);
                closeSidebar();
              }}
              className="cursor-pointer"
            >
              <div className="flex items-center gap-2 cursor-pointer">
                <div>
                  <StartChatIcon color={darkMode ? "#fff" : "#000"} />
                </div>
                <div className={`dark:text-white`}>Start New Chat</div>
              </div>
            </div>
          </div>
          {/* Conversation */}

          {isSidebarOpen && <ConversationItem collapsed={collapsed} />}

          {/* Theme Toggle */}
          <div className="flex justify-center px-4 py-5">
            <ToggleDarkModeComponent />
          </div>
        </div>
      )}
    </>
  );
};

export default LeftBar;
