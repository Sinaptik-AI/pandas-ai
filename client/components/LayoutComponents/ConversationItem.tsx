"use client";
import {
  ArchiveConversationApi,
  ConversationChatBySpaceApi,
} from "services/chatInterface";
import {
  FETCH_CONVERSATION,
  useConversationsContext,
} from "contexts/ConversationsProvider";
import { useRouter } from "next/navigation";
import React, { useCallback, useEffect, useState } from "react";
import { MdOutlineArchive } from "react-icons/md";
import { toast } from "react-toastify";
import { Tooltip } from "react-tooltip";
import { useAppStore } from "store";
import { isToday, isYesterday, startOfWeek, isWithinInterval } from "date-fns";
import { ConversationsHistoryLoader } from "components/Skeletons";
import ConfirmationDialog from "components/ConfirmationDialog";

interface IProps {
  collapsed: boolean;
}

const ConversationItem = ({ collapsed }: IProps) => {
  const setIsSidebarOpen = useAppStore((state) => state.setIsSidebarOpen);
  const [page, setPage] = useState(1);
  const itemsPerPage = 25;
  const [totalPages, setTotalPages] = useState(0);
  const spaceId = localStorage.getItem("spaceId");
  const [isLoading, setIsLoading] = useState(false);
  const [firstRender, setFirstRender] = useState(true);
  const [newConversations, setNewConversations] = useState([]);
  const darkMode = useAppStore((state) => state.darkMode);
  const { state, dispatch } = useConversationsContext();
  const router = useRouter();
  const [isModelOpen, setIsModelOpen] = useState(false);
  const [deleteLoader, setDeleteLoader] = useState(false);
  const [currentConversation, setCurrentConversation] = useState({
    conversationId: "",
    conversationDate: "",
  });

  const getAllConversations = useCallback(async () => {
    try {
      setIsLoading(true);
      const response = await ConversationChatBySpaceApi(
        spaceId,
        page,
        itemsPerPage
      );
      setTotalPages(Math.ceil(response?.data?.data?.count / itemsPerPage));
      setIsLoading(false);
      return response?.data?.data?.data;
    } catch (error) {
      toast.error("Something went wrong fetching conversations history!");
      console.log(JSON.stringify(error));
      setIsLoading(false);
    }
  }, [totalPages, page]);

  useEffect(() => {
    if (spaceId) {
      getAllConversations()
        .then((newConversations) => {
          setNewConversations(newConversations);
          setFirstRender(false);
        })
        .catch((error) => {
          console.log(JSON.stringify(error));
        });
    }
  }, [page]);

  useEffect(() => {
    const updatedConversations = [...state.conversations];

    newConversations?.forEach((conversation) => {
      const date = new Date(conversation.created_at);
      const formattedDate = formatDate(date);
      const existingGroupIndex = updatedConversations.findIndex(
        (group) => group.date === formattedDate
      );

      // Check if conversation already exists in updatedConversations
      const conversationExists = updatedConversations.some(
        (group) =>
          group.date === formattedDate &&
          group.conversations.some((conv) => conv.id === conversation.id)
      );

      if (existingGroupIndex === -1 && !conversationExists) {
        updatedConversations.push({
          date: formattedDate,
          conversations: [conversation],
        });
      } else if (!conversationExists) {
        updatedConversations[existingGroupIndex].conversations.push(
          conversation
        );
      }
    });
    dispatch({
      type: FETCH_CONVERSATION,
      payload: updatedConversations,
    });
  }, [newConversations]);

  const formatDate = (date) => {
    if (isToday(date)) {
      return "Today";
    } else if (isYesterday(date)) {
      return "Yesterday";
    } else {
      const startOfLastWeek = startOfWeek(new Date(), { weekStartsOn: 1 });
      if (isWithinInterval(date, { start: startOfLastWeek, end: new Date() })) {
        return "Last Week";
      } else {
        return "Older";
      }
    }
  };

  const handleScroll = (e) => {
    const bottom =
      e.target.scrollHeight - e.target.scrollTop <= e.target.clientHeight + 1;
    if (bottom && !isLoading && page < totalPages) {
      setPage((prevPage) => prevPage + 1);
    }
  };

  const confirmDelete = async () => {
    setDeleteLoader(true);
    await ArchiveConversationApi(currentConversation.conversationId)
      .then((response) => {
        toast.success(response?.data?.message);
        setIsModelOpen(false);
        handleOptimisticUpdate();
      })
      .catch((error) => {
        toast.error(
          error?.response?.data?.message
            ? error?.response?.data?.message
            : error.message
        );
      })
      .finally(() => setDeleteLoader(false));
  };

  const handleOptimisticUpdate = () => {
    const { conversationDate, conversationId } = currentConversation;
    const updatedConversations = state.conversations.map((conv) => {
      if (conv.date === conversationDate) {
        return {
          ...conv,
          conversations: conv.conversations.filter(
            (c) => c.id !== conversationId
          ),
        };
      }
      return conv;
    });

    dispatch({
      type: FETCH_CONVERSATION,
      payload: updatedConversations,
    });
  };
  const closeSidebar = () => {
    setIsSidebarOpen(false);
  };
  return (
    <>
      {firstRender && isLoading ? (
        <ConversationsHistoryLoader />
      ) : (
        <div
          className={`flex-1 custom-scroll ${
            collapsed ? "opacity-0 pointer-events-none" : "opacity-100"
          } transition-all duration-1000`}
          onScroll={handleScroll}
        >
          {state?.conversations?.map(({ date, conversations }) => (
            <div key={date}>
              <div className="dark:text-white font-bold text-base py-2">
                {date}
              </div>
              {conversations?.map((conversation) => (
                <div key={conversation.id} className="">
                  <div
                    className="py-1 dark:text-white text-base font-light truncate cursor-pointer group relative dark:hover:bg-[#11111180] hover:bg-[#EDEDED] rounded-lg"
                    onClick={() => {
                      router.push(
                        `/admin/conversations/chat-details?conversationId=${conversation?.id}&space_id=${conversation?.space?.id}`
                      );
                      closeSidebar();
                    }}
                    data-tooltip-id={`${conversation.id}`}
                  >
                    {conversation?.mesages?.[0]?.query}
                    <div
                      onClick={(e) => {
                        e.stopPropagation();
                        setIsModelOpen(true);
                        setCurrentConversation({
                          conversationDate: date,
                          conversationId: conversation.id,
                        });
                      }}
                      className="absolute flex justify-end pr-1 dark:bg-[#111111f2] bg-[#ededede6] w-10 right-0 top-1/2 transform -translate-y-1/2 opacity-0 group-hover:opacity-100 transition-opacity duration-300"
                    >
                      <MdOutlineArchive
                        color={darkMode ? "#fff" : "#000"}
                        size={20}
                      />
                    </div>
                  </div>
                  <Tooltip
                    id={`${conversation.id}`}
                    place="top-end"
                    className="z-50"
                    opacity={1}
                  >
                    {conversation?.mesages?.[0]?.query}
                  </Tooltip>
                </div>
              ))}
            </div>
          ))}
          {isLoading && <ConversationsHistoryLoader amount={1} />}

          {isModelOpen && (
            <ConfirmationDialog
              text={`Are you sure you want to archive this Conversation?`}
              onCancel={() => {
                setIsModelOpen(false);
              }}
              onSubmit={confirmDelete}
              isLoading={deleteLoader}
            />
          )}
        </div>
      )}
    </>
  );
};

export default ConversationItem;
