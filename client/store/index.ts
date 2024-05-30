import { ChatMessageData } from '@/types/chat-types';
import { create } from 'zustand'

type StoreType = {
    darkMode: boolean;
    toggleDarkMode: (e) => void;
    setSelectedChatItem?: (feedItem: ChatMessageData) => void;
    selectedChatItem?: ChatMessageData,
    isExplainViewOpen?: boolean;
    isChartEditOpen?: boolean;
    setIsExplainViewOpen?: (e: boolean) => void,
    setIsChartEditOpen?: (e: boolean) => void,
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
    setSelectedChatItem: (chatItem: ChatMessageData) => {
        set(() => ({ selectedChatItem: chatItem }));
    },
    setIsExplainViewOpen: (option: boolean) => {
        set(() => ({ isExplainViewOpen: option }));
    },
    setIsChartEditOpen: (option: boolean) => {
        set(() => ({ isChartEditOpen: option }));
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