import React from "react";
import { Poppins } from "next/font/google";
import { GoogleAnalytics } from "@next/third-parties/google";
import AppProvider from "@/Providers/AppProvider";
import { NEXT_PUBLIC_GOOGLE_ANALYTICS_ID } from "@/utils/constants";

const poppins = Poppins({
  subsets: ["latin"],
  weight: ["300", "400", "500", "600", "700"],
});

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className={poppins.className}>
        <AppProvider>{children}</AppProvider>
      </body>
      <GoogleAnalytics gaId={NEXT_PUBLIC_GOOGLE_ANALYTICS_ID} />
    </html>
  );
}
