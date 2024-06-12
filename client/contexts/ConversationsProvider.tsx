import React, { createContext, useContext, useReducer } from "react";

const initialState = {
  conversations: [],
};

export const FETCH_CONVERSATION = "FETCH_CONVERSATION";
export const UPDATE_CONVERSATION = "UPDATE_CONVERSATION";

const conversationsReducer = (state, action) => {
  switch (action.type) {
    case FETCH_CONVERSATION:
      return {
        conversations: action.payload,
      };
    case UPDATE_CONVERSATION:
      return {
        conversations: action.payload,
      };
    default:
      return state;
  }
};

const ConversationsContext = createContext(null);

export const ConversationsProvider = ({
  children,
}: {
  children: React.ReactNode;
}) => {
  const [state, dispatch] = useReducer(conversationsReducer, initialState);

  return (
    <ConversationsContext.Provider value={{ state, dispatch }}>
      {children}
    </ConversationsContext.Provider>
  );
};
export const useConversationsContext = () => useContext(ConversationsContext);
