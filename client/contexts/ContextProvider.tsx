"use client";
import React from "react";
import { ConversationsProvider } from "./ConversationsProvider";

const ContextProvider = ({ children }: { children: React.ReactNode }) => {
  return <ConversationsProvider>{children}</ConversationsProvider>;
};

export default ContextProvider;
