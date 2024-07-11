"use client";
import { isWindowAvailable } from "utils/navigation";
import React from "react";
import VerticalLineSeperator from "components/VerticalLineSeperator";
import Drawer from "react-modern-drawer";
import "react-modern-drawer/dist/index.css";
import { useAppStore } from "store";
import Navbar from "@/components/Navbar";
import SettingsLeftBar from "@/components/SettingsLayout/LeftBar";

export default function Admin({ children }: { children: React.ReactNode }) {
  const isSideBarOpen = useAppStore((state) => state.isSideBarOpen);
  const setIsSidebarOpen = useAppStore((state) => state.setIsSidebarOpen);

  if (isWindowAvailable()) document.documentElement.dir = "ltr";

  return (
    <>
      <div className="flex flex-col h-screen">
        <Navbar />
        <div className="flex h-screen dark:bg-black bg-white overflow-y-hidden">
          {/* Previous Conversations Sidebar */}
          <div className="hidden md:flex">
            <SettingsLeftBar />
            <VerticalLineSeperator />
          </div>

          {/* Main Content */}
          <div className="flex-1 w-full">{children}</div>
        </div>
      </div>
      <Drawer
        open={isSideBarOpen}
        onClose={() => setIsSidebarOpen(false)}
        direction="left"
        className=""
        zIndex={1000}
      >
        <SettingsLeftBar isMobileView={true} />
      </Drawer>
    </>
  );
}
