"use client";
import { isWindowAvailable } from "utils/navigation";
import React from "react";
import LeftBar from "components/LayoutComponents/LeftBar";
import VerticalLineSeperator from "components/VerticalLineSeperator";
import RightBar from "components/LayoutComponents/RightBar";
import Navbar from "components/Navbar";
import { useAppStore } from "store";
import Drawer from "react-modern-drawer";
import useWindowWidth from "hooks/useWindowWidth";
import "react-modern-drawer/dist/index.css";

export default function Admin({ children }: { children: React.ReactNode }) {
  if (isWindowAvailable()) document.documentElement.dir = "ltr";
  const isRightSidebarOpen = useAppStore((state) => state.isRightSidebarOpen);
  const setIsRightSidebarOpen = useAppStore(
    (state) => state.setIsRightSidebarOpen
  );
  const width = useWindowWidth();
  const isMobile = width <= 1200;

  return (
    <>
      <div className="flex flex-col h-screen">
        <Navbar />
        <div>
          <div className="flex h-[calc(100vh-75px)] dark:bg-black bg-white overflow-y-hidden">
            {/* Previous Conversations Sidebar */}
            <div className="flex">
              <LeftBar />
              <VerticalLineSeperator />
            </div>

            {/* Main Content */}
            <div className="flex-grow md:w-[calc(100%-370px)] xl:w-[calc(100%-690px)]">
              {children}
            </div>

            {/* Right Sidebar */}
            {/* <div className="hidden xl:flex">
              <VerticalLineSeperator />
              <RightBar />
            </div> */}
          </div>
        </div>
      </div>
      {isMobile && (
        <Drawer
          open={isRightSidebarOpen}
          onClose={() => setIsRightSidebarOpen(false)}
          direction="right"
          size={350}
        >
          <RightBar />
        </Drawer>
      )}
    </>
  );
}
