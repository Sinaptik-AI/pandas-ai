"use client";

import ChatSearchIcon from "components/Icons/ChatSearchIcon";
import { useRouter } from "next/navigation";
import React from "react";
import { ROUTE_CHAT_SCREEN } from "utils/constants";

interface IProps {
  queryRef: React.RefObject<HTMLInputElement>;
  sendQuery?: boolean;
  onNewMessage?: (message: string) => void;
  extra?: string;
  handleSearch?: (e) => void;
  handleKeyDown?: (e) => void;
  type?: "feed" | "chat";
  isAutoCompleteOpen?: boolean;
}

const ChatInput = ({
  queryRef,
  sendQuery = false,
  onNewMessage,
  extra,
  handleKeyDown,
  handleSearch,
  type = "chat",
  isAutoCompleteOpen,
}: IProps) => {
  const router = useRouter();

  return (
    <form
      className={`w-full ${extra}`}
      onSubmit={(e) => {
        e.preventDefault();
        if (onNewMessage) onNewMessage(queryRef.current.value);
        if (type === "feed") {
          router.push(ROUTE_CHAT_SCREEN);
          localStorage.setItem("searchQuery", queryRef.current.value);
        }
      }}
    >
      <div className="relative">
        <input
          type="text"
          ref={queryRef}
          className={`w-full text-dark dark:text-white dark:bg-[#333333] font-montserrat font-normal pl-5 pr-[40px] 
          focus:outline-none py-3 text-md placeholder-darkMain dark:placeholder-white/40 shadow-md border border-gray-100 dark:border-none
          ${isAutoCompleteOpen ? "rounded-t-[18px]" : "rounded-[25px]"}`}
          placeholder="Enter your message"
          autoComplete="off"
          disabled={sendQuery}
          onKeyDown={handleKeyDown}
          onChange={handleSearch}
        />
        <span className="absolute inset-y-0 right-0 flex items-center pr-4">
          <button
            type="submit"
            disabled={sendQuery}
            className="focus:outline-none focus:shadow-outline"
          >
            <ChatSearchIcon />
          </button>
        </span>
      </div>
    </form>
  );
};

export default ChatInput;
