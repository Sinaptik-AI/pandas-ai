import React from "react";
import VerticalLineSeperator from "components/VerticalLineSeperator";
import Navbar from "@/components/Navbar";
import SettingsLeftBar from "@/components/SettingsLayout/LeftBar";
import LeftBarDrawer from "@/components/SettingsLayout/LeftBarDrawer";

export default async function SettingsLayout({
  children,
}: {
  children: React.ReactNode;
}) {
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
      <LeftBarDrawer />
    </>
  );
}
