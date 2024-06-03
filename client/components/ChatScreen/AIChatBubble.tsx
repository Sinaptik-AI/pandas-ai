import React, { useRef, memo, useState } from "react";
import Image from "next/image";
import panda from "public/svg/panda.svg";
import { ChatMessageData } from "@/types/chat-types";
import ChatDataFrame from "./ChatDataFrame";
import ChatPlot from "./ChatPlot";
import ChatReaction from "./ChatReaction";
import EditCodeComponent from "./EditCode";
import { ChatMessageRetry, ChatReactionApi, EditCode } from "services/chat";
import { toast } from "react-toastify";
import { ChatReactionLoader } from "components/Skeletons";
import ExplainView from "./ExplainView";
import { useAppStore } from "store";

interface IProps {
  chat: ChatMessageData;
  lastIndex?: boolean;
  chatData: ChatMessageData[];
  setChatData: (e) => void;
}

const AIChatBubble = ({ chat, chatData, setChatData, lastIndex }: IProps) => {
  const childRef = useRef(null);
  const selectedChatItem = useAppStore((state) => state.selectedChatItem);
  const isExplainViewOpen = useAppStore((state) => state.isExplainViewOpen);
  const setIsExplainViewOpen = useAppStore(
    (state) => state.setIsExplainViewOpen
  );
  const [codeEditLoader, setCodeEditLoader] = useState(false);
  const [iscodeViewOpen, setIscodeViewOpen] = useState(false);
  const [codeValue, setCodeValue] = useState("");
  const [reactionLoading, setReactionLoading] = useState(false);

  const [updateId, setUpdateId] = useState({
    reaction_id: "",
    message_id: "",
  });

  const handleCodeView = async (id) => {
    const filteredData = chatData?.find((data) => {
      return data?.id === id;
    });
    setUpdateId({
      message_id: filteredData?.id,
      reaction_id: filteredData?.reaction_id,
    });
    setCodeValue(filteredData?.code);
    setIscodeViewOpen(true);
  };

  const handleCodeUpdate = async () => {
    try {
      setCodeEditLoader(true);
      const payload = {
        code: codeValue,
      };
      const response = await EditCode(updateId?.message_id, payload);
      if (response?.status === 200) {
        const updatedCode = chatData?.map((data) => {
          return data.id == updateId?.message_id
            ? {
                ...data,
                code: response?.data?.data?.training_data?.code,
                response: response?.data?.data?.response,
              }
            : data;
        });
        setIscodeViewOpen(false);
        setCodeEditLoader(false);
        setChatData(updatedCode);
      } else {
        setCodeEditLoader(false);
        setIscodeViewOpen(false);
        toast.error(response?.data?.data?.message);
      }
    } catch (error) {
      setCodeEditLoader(false);
      console.log(error);
    }
  };

  const handleUserRating = async (id: string, reaction: boolean) => {
    const updatedData = chatData?.map((data) => {
      return data?.id === id ? { ...data, thumbs_up: reaction } : data;
    });
    setChatData(updatedData);

    await ChatReactionApi(id, { thumbs_up: reaction }).catch((error) => {
      const updatedData = chatData?.map((data) => {
        return data?.id === id ? { ...data, thumbs_up: !reaction } : data;
      });
      setChatData(updatedData);

      toast.error(
        error?.response?.data?.message
          ? error?.response?.data?.message
          : error.message
      );
    });
  };

  const handleRetry = async (id) => {
    const filteredData = chatData?.find((data) => {
      return data?.id === id;
    });
    setUpdateId({
      message_id: filteredData?.id,
      reaction_id: filteredData?.reaction_id,
    });
    setReactionLoading(true);
    await ChatMessageRetry(id)
      .then((response) => {
        const updatedData = chatData?.map((data) => {
          return data?.id === id
            ? {
                ...data,
                thumbs_up: response?.data?.data?.user_rating?.thumbs_up,
                reaction_id: response?.data?.data?.user_rating?.id,
                response: response?.data?.data?.response,
                code: response?.data?.data?.code,
              }
            : data;
        });
        setChatData(updatedData);
      })
      .catch((error) => {
        toast.error(
          error?.response?.data?.message
            ? error?.response?.data?.message
            : error.message
        );
      })
      .finally(() => setReactionLoading(false));
  };

  const handleMouseEnter = () => {
    if (!lastIndex) {
      if (childRef?.current) {
        childRef.current.style.visibility = "visible";
      }
    }
  };

  const handleMouseLeave = () => {
    if (!lastIndex) {
      if (childRef?.current) {
        childRef.current.style.visibility = "hidden";
      }
    }
  };

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

        <div
          className="flex flex-1 flex-col"
          onMouseEnter={handleMouseEnter}
          onMouseLeave={handleMouseLeave}
        >
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
            <>
              {iscodeViewOpen && chat?.id === updateId?.message_id ? (
                <EditCodeComponent
                  closeEditor={() => setIscodeViewOpen(false)}
                  codeValue={codeValue}
                  setCodeValue={setCodeValue}
                  handleCodeUpdate={handleCodeUpdate}
                  isLoading={codeEditLoader}
                />
              ) : isExplainViewOpen && chat?.id === selectedChatItem?.id ? (
                <ExplainView closeEditor={() => setIsExplainViewOpen(false)} />
              ) : (
                typeof chat.response !== "string" &&
                chat?.response?.map((response, indx) => (
                  <div className="w-full" key={indx}>
                    {reactionLoading && chat?.id === updateId?.message_id ? (
                      <ChatReactionLoader />
                    ) : (
                      <React.Fragment key={indx}>
                        {response?.type === "dataframe" ? (
                          response?.value?.headers?.length > 0 &&
                          response?.value?.rows?.length > 0 ? (
                            <>
                              <ChatDataFrame
                                chatResponse={response}
                                chatId={chat.id}
                                index={indx}
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
                    )}
                  </div>
                ))
              )}
            </>
            <div
              ref={childRef}
              className="mt-2"
              style={{ visibility: lastIndex ? "visible" : "hidden" }}
            >
              {chat?.code && (
                <ChatReaction
                  chat={chat}
                  handleCodeView={handleCodeView}
                  handleRetry={handleRetry}
                  handleUserRating={handleUserRating}
                />
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default memo(AIChatBubble);
