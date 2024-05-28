"use client";
import React from "react";
import { ConversationsProvider } from "./ConversationsProvider";
import { FeedsProvider } from "./FeedsProvider";

const ContextProvider = ({ children }: { children: React.ReactNode }) => {
  return (
    <ConversationsProvider>
      <FeedsProvider>{children}</FeedsProvider>
    </ConversationsProvider>
  );
};

export default ContextProvider;
