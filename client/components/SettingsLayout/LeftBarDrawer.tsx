"use client";
import { useAppStore } from "@/store";
import React from "react";
import Drawer from "react-modern-drawer";
import SettingsLeftBar from "./LeftBar";
import "react-modern-drawer/dist/index.css";

const LeftBarDrawer = () => {
  const isSideBarOpen = useAppStore((state) => state.isSideBarOpen);
  const setIsSidebarOpen = useAppStore((state) => state.setIsSidebarOpen);
  return (
    <>
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
};

export default LeftBarDrawer;
