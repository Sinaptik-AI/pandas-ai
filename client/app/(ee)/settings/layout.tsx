import React from "react";
import SettingsLayout from "@/app/settings/layout";

export default function EESettingsLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return <SettingsLayout>{children}</SettingsLayout>;
}
