import React, { memo } from "react";
import Image from "next/image";
import panda from "public/svg/panda.svg";
import { ChatMessageData } from "@/types/chat-types";
import ChatDataFrame from "./ChatDataFrame";
import ChatPlot from "./ChatPlot";

interface IProps {
  chat: ChatMessageData;
  lastIndex?: boolean;
}

const AIChatBubble = ({ chat, lastIndex }: IProps) => {
  const checkType = (type: string) => {
    if (typeof chat.response !== "string") {
      return chat?.response?.every((item) => item?.type === type);
    }
  };
  const isMultiple = () => {
    return chat?.response?.length > 1;
  };

  return (
    <div
      className={`border-b border-b-[#333333] ${
        lastIndex && "border-none"
      } pb-5`}
    >
      <div className="flex w-full font-montserrat gap-4">
        <div className="flex h-7 w-7 md:h-10 md:w-10 rounded-full overflow-hidden bg-[#191919] text-white flex-shrink-0">
          <Image
            src={panda}
            alt="logo"
            className="h-7 w-7 md:h-10 md:w-10  rounded-full"
          />
        </div>

        <div className="flex w-full flex-col">
          <span className="dark:text-white font-bold text-lg">PandaBI</span>
          <div
            className={`break-all text-sm md:text-[15px] font-medium w-auto overflow-visible dark:text-white
                              ${checkType("plot") ? "w-full h-full" : ""}
                              ${checkType("dataframe") ? "w-11/12 h-full" : ""}
                              ${
                                chat?.error
                                  ? "text-red-600 bg-red-200"
                                  : " font-normal"
                              }`}
          >
            {typeof chat.response !== "string" &&
              chat?.response?.map((response, indx) => (
                <div className="w-full" key={indx}>
                  <React.Fragment key={indx}>
                    {response?.type === "dataframe" ? (
                      response?.value?.headers?.length > 0 &&
                      response?.value?.rows?.length > 0 ? (
                        <>
                          <ChatDataFrame
                            chatResponse={response}
                            chatId={chat.id}
                            key={chat?.id}
                          />
                        </>
                      ) : (
                        <p>No Table data available</p>
                      )
                    ) : response?.type === "plot" ? (
                      <ChatPlot
                        chatResponse={response}
                        plotSettings={chat?.plotSettings}
                        key={chat?.id}
                      />
                    ) : response?.type === "string" ? (
                      <div
                        className={`text-lg whitespace-pre-line ${
                          isMultiple()
                            ? "my-5 break-all font-normal w-auto overflow-visible"
                            : ""
                        }`}
                      >
                        {response?.message}
                      </div>
                    ) : response.type === "number" ? (
                      <h1 className="font-bold text-4xl py-4 px-3">
                        {response?.value as string}
                      </h1>
                    ) : (
                      ""
                    )}

                    <div className="whitespace-pre-wrap break-all"></div>
                  </React.Fragment>
                </div>
              ))}
          </div>
        </div>
      </div>
    </div>
  );
};

export default memo(AIChatBubble);
