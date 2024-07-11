"use client";
import React, { ReactNode, useEffect } from "react";
import ContextProvider from "@/contexts/ContextProvider";
import { usePathname } from "next/navigation";
import dynamic from "next/dynamic";
import { getTitleFromPath } from "@/utils/getTitleFromPath";
import {
  NEXT_PUBLIC_INTERCOM_APP_ID,
  NEXT_PUBLIC_MIXPANEL_TOKEN,
  NEXT_PUBLIC_ROLLBAR_CLIENT_TOKEN,
} from "@/utils/constants";
import mixpanel from "mixpanel-browser";
import { Provider as RollbarProvider, ErrorBoundary } from "@rollbar/react";
import QueryProvider from "./QueryProvider";
import Intercom from "@/components/Intercom/Intercom";
import { ToastContainer } from "react-toastify";
import "styles/globals.css";
import "styles/App.css";
import "styles/multi-range-slider.css";
import "react-toastify/dist/ReactToastify.css";

const _NoSSR = ({ children }) => <React.Fragment>{children}</React.Fragment>;
const NoSSR = dynamic(() => Promise.resolve(_NoSSR), {
  ssr: false,
});

export default function AppProvider({ children }: { children: ReactNode }) {
  const pathname = usePathname();
  const defaultTitle = getTitleFromPath(pathname);

  const rollbarConfig = {
    accessToken: NEXT_PUBLIC_ROLLBAR_CLIENT_TOKEN,
    environment: process.env.NODE_ENV || "development",
  };

  useEffect(() => {
    document.title = `${defaultTitle} | PandaBI`;
  }, [defaultTitle]);

  useEffect(() => {
    mixpanel.init(NEXT_PUBLIC_MIXPANEL_TOKEN, {
      autotrack: true,
      track_pageview: true,
    });
  }, []);
  return (
    <>
      <RollbarProvider config={rollbarConfig}>
        <ErrorBoundary>
          <ContextProvider>
            <NoSSR>
              <ToastContainer autoClose={3000} className="w-64 text-white" />
              <QueryProvider>{children}</QueryProvider>
            </NoSSR>
          </ContextProvider>
        </ErrorBoundary>
      </RollbarProvider>
      <Intercom appID={NEXT_PUBLIC_INTERCOM_APP_ID} />
    </>
  );
}
