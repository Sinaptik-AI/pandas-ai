"use client";
import { ChatApi } from "services/chat";
import React, { useState, useEffect, useRef } from "react";
import { ChatMessageData } from "../../../types/chat-types";
import { useSearchParams } from "next/navigation";
import { toast } from "react-toastify";
import ChatScreen from "components/ChatScreen";
import {
  UPDATE_CONVERSATION,
  useConversationsContext,
} from "contexts/ConversationsProvider";
import mixpanel from "mixpanel-browser";
import { reorderArray } from "utils/reorderConversations";
import { appendQueryParamtoURL } from "utils/appendQueryParamtoURL";
import { useAppStore } from "store";
import { ConversationMessages } from "@/services/conversations";

const ChatPage = () => {
  const params = useSearchParams();
  const conversation_id = params.get("conversationId");

  const [conversationId, setConversationId] = useState<string>(
    conversation_id || ""
  );
  const [sendQuery, setSendQuery] = useState(false);
  const [chat, setChat] = useState<ChatMessageData[]>([]);
  const [isTyping, setIsTyping] = useState<boolean>(false);
  const setIsNewChatClicked = useAppStore((state) => state.setIsNewChatClicked);
  const isNewChatClicked = useAppStore((state) => state.isNewChatClicked);

  const [scrollLoad, setScrollLoad] = useState(false);
  const [rawApiData, setRawApiData] = useState([]);
  const [hasMore, setHasMore] = useState(false);
  const [mounted, setMounted] = useState(true);
  const [isGetConversationsLoading, setIsGetConversationsLoading] =
    useState(false);

  const queryRef = useRef(null);
  const spaceId = localStorage.getItem("spaceId");
  const firstRequest = React.useRef(false);
  const searchQuery = localStorage.getItem("searchQuery");
  const { state, dispatch } = useConversationsContext();

  const rawApiDataLengthRef = useRef(rawApiData.length);
  const scrollDivRef = useRef(null);
  const firstRender = useRef(false);

  useEffect(() => {
    if (queryRef.current) {
      queryRef.current.focus();
    }
  }, []);

  useEffect(() => {
    if (sendQuery) {
      const query = queryRef.current.value;
      chat.push({
        space_id: spaceId,
        conversation_id: conversationId,
        query: query,
      });
      setIsTyping(true);
      setChat(chat);
      process.nextTick(() => {
        scrollToBottom();
      });
      fetchChatData(queryRef.current.value);
      queryRef.current.value = "";
    }
  }, [sendQuery]);

  useEffect(() => {
    if (searchQuery) {
      chat.push({
        space_id: spaceId,
        conversation_id: conversationId,
        query: searchQuery,
      });
      setIsTyping(true);
      setChat(chat);
      fetchChatData(searchQuery);
      localStorage.removeItem("searchQuery");
    }
  }, []);

  const fetchChatData = async (userQuery: string) => {
    await ChatApi({
      workspace_id: spaceId,
      conversation_id: conversationId,
      query: userQuery,
    })
      .then((response) => {
        const conId = response?.data?.data?.conversation_id;
        const messageId = response?.data?.data?.message_id;
        const responseQuery = response?.data?.data?.query;
        const code = response?.data?.data?.code;
        mixpanel.track("New Chat Message", { userQuery: userQuery });

        if (response?.data?.data?.response) {
          chat.push({
            response: response?.data?.data?.response,
            id: messageId,
            thumbs_up: null,
            code,
            reaction_id: null,
            space_id: spaceId,
            conversation_id: conId,
          });
          if (!firstRequest.current && !conversation_id) {
            AddNewMessageToConversations(conId, messageId, responseQuery);
            firstRequest.current = true;
            appendQueryParamtoURL(`conversationId=${conId}`);
          }
        } else {
          chat.push({
            response: response?.data?.data,
            thumbs_up: null,
            reaction_id: null,
            space_id: spaceId,
            conversation_id: conversationId,
            code: null,
          });
        }
        setConversationId(conId);
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

  const AddNewMessageToConversations = (
    conId: string,
    messageId: string,
    query: string
  ) => {
    const newConversations = state?.conversations;
    const today = new Date().toISOString();
    const newMessage = {
      id: messageId,
      query,
    };
    const todayIndex = newConversations.findIndex(
      (entry) => entry.date === "Today"
    );
    if (todayIndex !== -1) {
      const todayConversations = newConversations[todayIndex].conversations;
      todayConversations.unshift({
        id: conId,
        space_id: spaceId,
        user_id: null,
        created_at: today,
        space: {
          id: spaceId,
        },
        messages: [newMessage],
      });
    } else {
      newConversations.unshift({
        date: "Today",
        conversations: [
          {
            id: conId,
            space_id: spaceId,
            user_id: null,
            created_at: today,
            space: {
              id: spaceId,
            },
            messages: [newMessage],
          },
        ],
      });
    }
    dispatch({
      type: UPDATE_CONVERSATION,
      payload: newConversations,
    });
  };

  useEffect(() => {
    if (conversation_id) {
      fetchConversationHistory([], []);
    }
  }, []);

  const fetchConversationHistory = async (NewChat, newRawApiData) => {
    if (NewChat?.length < 1) {
      setScrollLoad(true);
    }

    setIsGetConversationsLoading(true);
    await ConversationMessages(conversation_id)
      .then((response) => {
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
              conversation_id: conversationId,
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
              conversation_id: conversationId,
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
        setIsGetConversationsLoading(false);
      });
  };

  useEffect(() => {
    // state cleanup
    if (isNewChatClicked) {
      setConversationId("");
      setSendQuery(false);
      setChat([]);
      setIsTyping(false);
      setRawApiData([]);
      setHasMore(false);
      setMounted(true);
      firstRequest.current = false;
      setIsNewChatClicked(false);
      firstRender.current = false;
    }
  }, [isNewChatClicked]);

  const scrollToBottom = () => {
    if (scrollDivRef.current) {
      scrollDivRef.current.scrollTop = scrollDivRef.current.scrollHeight;
    }
  };

  return (
    <div className="flex text-gray-800 h-full w-full">
      <ChatScreen
        chatData={chat}
        setChatData={setChat}
        isTyping={isTyping}
        sendQuery={sendQuery}
        queryRef={queryRef}
        setSendQuery={setSendQuery}
        scrollLoad={scrollLoad}
        loading={isGetConversationsLoading && mounted}
        hasMore={hasMore}
        scrollDivRef={scrollDivRef}
      />
    </div>
  );
};
export default ChatPage;
