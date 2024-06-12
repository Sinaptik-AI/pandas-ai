"use client";
import { ChatApi } from "services/chat";
import React, { useState, useEffect, useRef } from "react";
import { useRouter } from "next/navigation";
import { useParams } from "next/navigation";
import { ChatMessageData } from "@/types/chat-types";
import { toast } from "react-toastify";
import ChatScreen from "components/ChatScreen";
import { reorderArray } from "utils/reorderConversations";
import { ConversationMessages } from "@/services/conversations";

const ChatDetails = () => {
  const rowsPerPage = 8;
  const [sendQuery, setSendQuery] = useState(false);
  const [chat, setChat] = useState<ChatMessageData[]>([]);
  const [isTyping, setIsTyping] = useState<boolean>(false);
  const [currentPage, setCurrentPage] = useState(1);
  const [scrollLoad, setScrollLoad] = useState(false);
  const [rawApiData, setRawApiData] = useState([]);
  const [hasMore, setHasMore] = useState(false);
  const [mounted, setMounted] = useState(true);
  const [totalPages, setTotalPages] = useState(1);
  const [skip, setSkip] = useState(0);
  const [isLoading, setIsLoading] = useState(true);
  const firstRender = useRef(false);

  const router = useRouter();

  const params: { id: string } = useParams();
  const conversation_id = params.id;
  const space_id = localStorage.getItem("spaceId");

  const rawApiDataLengthRef = useRef(rawApiData.length);
  const scrollDivRef = useRef(null);
  const queryRef = useRef(null);

  useEffect(() => {
    rawApiDataLengthRef.current = rawApiData.length;
  }, [rawApiData]);

  const fetchConversationHistory = async (
    NewChat,
    newRawApiData,
    skip: number
  ) => {
    if (NewChat?.length < 1) {
      setScrollLoad(true);
    }

    setIsLoading(true);
    await ConversationMessages(conversation_id, skip, rowsPerPage)
      .then((response) => {
        const totalCount = response.data?.data?.count;
        if (mounted) {
          setTotalPages(Math.ceil(totalCount / rowsPerPage));
        }

        const responseData = response?.data?.data?.messages;

        if (responseData != undefined) {
          setRawApiData([...newRawApiData, ...responseData]);
        }
        const conversation_history_query = response?.data?.data?.messages?.map(
          (data) => {
            return {
              query: data?.query,
              createdAt: data?.created_at,
              id: `${data.id}1`,
              conversation_id: conversation_id,
            };
          }
        );
        const conversation_history_resp = response?.data?.data?.messages?.map(
          (data) => {
            return {
              response: data?.response,
              createdAt: data?.created_at,
              id: data.id,
              code: data?.code_generated,
              conversation_id: conversation_id,
              thumbs_up: data?.user_rating,
              plotSettings: data?.settings,
            };
          }
        );
        let conversation_history = conversation_history_query != undefined && [
          ...conversation_history_query,
          ...conversation_history_resp,
        ];
        conversation_history = reorderArray(conversation_history);
        setMounted(false);
        setChat([...conversation_history, ...NewChat]);
        firstRender.current = true;
        rawApiDataLengthRef.current = newRawApiData.length;
        localStorage.setItem("prevConversationId", conversation_id);
      })
      .catch((error) => {
        toast.error(
          error?.response?.data?.message
            ? error.response.data.message
            : error.message
        );
      })
      .finally(() => {
        setHasMore(false);
        setScrollLoad(false);
        setIsLoading(false);
        process.nextTick(() => {
          scrollToBottom();
        });
      });
  };

  const handleScroll = (e) => {
    const target = e.target;
    if (target.scrollTop === 0 && !scrollLoad) {
      if (currentPage < totalPages) {
        setHasMore(true);
        setCurrentPage((prevPage) => prevPage + 1);
        setSkip(currentPage * rowsPerPage);
      }
    }
  };

  useEffect(() => {
    if (firstRender?.current) {
      if (Number(rawApiDataLengthRef.current) <= rowsPerPage) {
        const scrollDiv = document.getElementById("chat-div");
        // scrollDiv.scrollTop = 90;
        if (scrollDiv) {
          scrollDiv.scrollTop = scrollDiv.scrollHeight;
          firstRender.current = false;
        }
      }
    }
  }, [chat]);

  useEffect(() => {
    const scrollDiv = document.getElementById("chat-div");

    if (scrollDiv) {
      scrollDiv.addEventListener("scroll", handleScroll);

      return () => {
        scrollDiv.removeEventListener("scroll", handleScroll);
      };
    }
  }, [currentPage, totalPages]);

  useEffect(() => {
    const fetchDataOnScroll = async () => {
      if (!mounted) {
        const scrollDiv = document.getElementById("chat-div");

        // Store previous scroll height and current scroll position
        const previousScrollHeight = scrollDiv.scrollHeight;
        const previousScrollTop = scrollDiv.scrollTop;

        fetchConversationHistory(chat, rawApiData, skip).then(() => {
          process.nextTick(() => {
            scrollDiv.classList.remove("chat-div");
            scrollDiv.scrollTop =
              scrollDiv.scrollHeight - previousScrollHeight + previousScrollTop;
          });
        });
      }
    };

    fetchDataOnScroll();
  }, [currentPage]);

  useEffect(() => {
    fetchConversationHistory([], [], 0);
  }, [conversation_id, space_id]);

  useEffect(() => {
    if (sendQuery) {
      const query = queryRef?.current?.value;
      chat.push({
        space_id: space_id,
        conversation_id: conversation_id,
        query: query,
      });
      setIsTyping(true);
      setChat(chat);
      process.nextTick(() => {
        scrollToBottom();
      });
      const fetchChatData = async () => {
        await ChatApi({
          workspace_id: space_id,
          conversation_id: conversation_id,
          query: query,
        })
          .then((response) => {
            const conId = response?.data?.data?.conversation_id;
            const messageId = response?.data?.data?.message_id;
            const code = response?.data?.data?.code;
            if (response?.data?.data?.response) {
              chat.push({
                response: response?.data?.data?.response,
                id: messageId,
                thumbs_up: null,
                code,
                reaction_id: null,
                space_id: response?.data?.data?.space_id,
                conversation_id: conId,
              });
            } else {
              chat.push({
                response: response?.data?.data,
                thumbs_up: null,
                reaction_id: null,
                space_id: space_id,
                conversation_id: conversation_id,
                code: null,
              });
            }
            setChat([...chat]);
          })
          .catch((error) => {
            console.log(JSON.stringify(error));
            toast.error(
              error?.response?.data?.message
                ? error?.response?.data?.message
                : error?.message
            );
          })
          .finally(() => {
            setSendQuery(false);
            setIsTyping(false);
            process.nextTick(() => {
              scrollToBottom();
            });
          });
      };
      fetchChatData();
      queryRef!.current!.value = "";
    }
  }, [sendQuery]);

  if (!conversation_id && !space_id) {
    return router.push(`/admin/chat`);
  }
  const scrollToBottom = () => {
    if (scrollDivRef.current) {
      scrollDivRef.current.scrollTop = scrollDivRef.current.scrollHeight;
    }
  };

  return (
    <div className="flex text-gray-800 h-full w-full">
      <ChatScreen
        scrollLoad={scrollLoad}
        chatData={chat}
        setChatData={setChat}
        isTyping={isTyping}
        queryRef={queryRef}
        sendQuery={sendQuery}
        setSendQuery={setSendQuery}
        hasMore={hasMore}
        scrollDivRef={scrollDivRef}
        loading={isLoading && mounted}
      />
    </div>
  );
};
export default ChatDetails;
