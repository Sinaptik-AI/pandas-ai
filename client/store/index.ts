import { ChatMessageData } from '@/types/chat-types';
import { FeedMessage } from '@/components/FeedsScreen.tsx/types';
import { create } from 'zustand'

type StoreType = {
    darkMode: boolean;
    toggleDarkMode: (e) => void;
    setSelectedFeedItem?: (feedItem: FeedMessage) => void;
    selectedFeedItem?: FeedMessage
    setSelectedChatItem?: (feedItem: ChatMessageData) => void;
    setSelectedChartItem?: (chartItem: FeedMessage) => void,
    selectedChatItem?: ChatMessageData,
    isExplainViewOpen?: boolean;
    isChartEditOpen?: boolean;
    setIsExplainViewOpen?: (e: boolean) => void,
    setIsChartEditOpen?: (e: boolean) => void,
    selectedChartItem?: FeedMessage;
    isSideBarOpen?: boolean;
    setIsSidebarOpen?: (e: boolean) => void;
    isNewChatClicked?: boolean;
    setIsNewChatClicked?: (e: boolean) => void;
    isRightSidebarOpen?: boolean;
    setIsRightSidebarOpen?: (e: boolean) => void;
    isFeedFilterOpen?: boolean
    setIsFeedFilterOpen?: (e: boolean) => void;
}

export const useAppStore = create<StoreType>((set) => ({
    darkMode: false,
    selectedFeedItem: {},
    selectedChatItem: {},
    isExplainViewOpen: false,
    isChartEditOpen: false,
    selectedChartItem: {},
    isSideBarOpen: false,
    isNewChatClicked: false,
    isRightSidebarOpen: false,
    isFeedFilterOpen: false,

    toggleDarkMode: (mode) => {
        set(() => ({ darkMode: mode }))
    },
    setSelectedFeedItem: (feedItem: FeedMessage) => {
        set(() => ({ selectedFeedItem: feedItem }));
    },
    setSelectedChatItem: (chatItem: ChatMessageData) => {
        set(() => ({ selectedChatItem: chatItem }));
    },
    setIsExplainViewOpen: (option: boolean) => {
        set(() => ({ isExplainViewOpen: option }));
    },
    setIsChartEditOpen: (option: boolean) => {
        set(() => ({ isChartEditOpen: option }));
    },
    setSelectedChartItem: (chartItem: FeedMessage) => {
        set(() => ({ selectedChartItem: chartItem }));
    },
    setIsSidebarOpen: (option: boolean) => {
        set(() => ({ isSideBarOpen: option }));
    },
    setIsNewChatClicked: (option: boolean) => {
        set(() => ({ isNewChatClicked: option }));
    },
    setIsRightSidebarOpen: (option: boolean) => {
        set(() => ({ isRightSidebarOpen: option }));
    },
    setIsFeedFilterOpen: (option: boolean) => {
        set(() => ({ isFeedFilterOpen: option }));
    },
}))