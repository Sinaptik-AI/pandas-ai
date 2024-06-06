"use client";
import React from "react";
import Image from "next/image";
import ChatLoader from "components/ChatLoader/page";
import panda from "public/svg/panda.svg";
import { ChatScreenProps } from "./chat-types";
import ChatInput from "./ChatInput";
import UserChatBubble from "./UserChatBubble";
import AIChatBubble from "./AIChatBubble";
import { ChatPlaceholderLoader } from "components/Skeletons";

const ChatScreen = ({
  scrollLoad,
  chatData,
  isTyping,
  queryRef,
  sendQuery,
  setSendQuery,
  hasMore,
  loading,
  scrollDivRef,
}: ChatScreenProps) => {
  const handleNewMessage = () => {
    setSendQuery(true);
  };

  return (
    <div className="flex antialiased text-gray-800 w-full">
      <div className="flex flex-col flex-auto flex-shrink-0 rounded-2xl h-full dark:!bg-[#000] w-[calc(100vw-22px)] md:w-full">
        <div
          className="flex flex-col h-full overflow-x-scroll mb-4 custom-scroll chat-div"
          id="chat-div"
          ref={scrollDivRef}
        >
          <div className="mx-auto w-full max-w-[900px]">
            <div
              className="flex flex-col flex-auto px-2 md:px-4"
              style={{ marginTop: "1rem" }}
            >
              <div
                className="flex flex-col flex-auto flex-shrink-0 gap-4 rounded-2xl h-full md:p-4 dark:!bg-[#000]"
                id="scrollableDiv"
              >
                {scrollLoad ? (
                  <ChatPlaceholderLoader />
                ) : (
                  <>
                    {hasMore && (
                      <div className="flex justify-center items-center">
                        <ChatPlaceholderLoader />
                      </div>
                    )}
                    {loading ? (
                      <ChatPlaceholderLoader />
                    ) : (
                      <>
                        {chatData?.length === 0 && (
                          <h3 className="flex items-center justify-center w-full h-full m-auto dark:text-white text-xl font-montserrat">
                            How can I help you today?
                          </h3>
                        )}
                        {chatData?.map((chat, chatIndex) => (
                          <div key={chat.id}>
                            {chat?.query ? (
                              <UserChatBubble query={chat?.query} />
                            ) : (
                              <AIChatBubble
                                key={chat.id}
                                chat={chat}
                                lastIndex={chatData?.length - 1 === chatIndex}
                              />
                            )}
                          </div>
                        ))}
                        {isTyping && (
                          <>
                            <div className="col-start-1 col-end-8 p-3 rounded-lg">
                              <div className="flex flex-row items-center gap-2">
                                <div className="flex justify-center h-10 rounded-full bg-[#191919] text-white flex-shrink-0">
                                  <Image
                                    src={panda}
                                    alt="logo"
                                    className="h-7 w-7 md:h-10 md:w-10 rounded-full"
                                  />
                                </div>
                                <div className="relative mr-3 text-sm py-2 bg-white shadow rounded-xl">
                                  <div>
                                    <ChatLoader />
                                  </div>
                                </div>
                              </div>
                            </div>
                          </>
                        )}
                      </>
                    )}
                  </>
                )}
              </div>
            </div>
          </div>
        </div>
        <div className="mx-auto w-full max-w-[900px]">
          <ChatInput
            onNewMessage={handleNewMessage}
            queryRef={queryRef}
            sendQuery={sendQuery}
            extra="px-2 md:px-6 pb-4"
          />
        </div>
      </div>
    </div>
  );
};

export default ChatScreen;
