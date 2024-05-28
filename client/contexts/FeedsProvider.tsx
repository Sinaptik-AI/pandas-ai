import { FeedMessage } from "components/FeedsScreen.tsx/types";
import React, { createContext, useContext, useReducer } from "react";

interface IFeedsState {
  feeds: FeedMessage[];
}

type FeedsAction = {
  type: string;
  payload: FeedMessage[];
};

const initialState: IFeedsState = {
  feeds: [],
};

export const UPDATE_FEEDS = "UPDATE_FEEDS";

const feedsReducer = (state: IFeedsState, action: FeedsAction): IFeedsState => {
  switch (action.type) {
    case UPDATE_FEEDS:
      return {
        feeds: action.payload,
      };
    default:
      return state;
  }
};

interface FeedsContextType {
  state: IFeedsState;
  dispatch: React.Dispatch<FeedsAction>;
}

const FeedsContext = createContext<FeedsContextType | null>(null);

export const FeedsProvider: React.FC<{ children: React.ReactNode }> = ({
  children,
}) => {
  const [state, dispatch] = useReducer(feedsReducer, initialState);

  return (
    <FeedsContext.Provider value={{ state, dispatch }}>
      {children}
    </FeedsContext.Provider>
  );
};

export const useFeedsContext = (): FeedsContextType => {
  const context = useContext(FeedsContext);
  if (!context) {
    throw new Error("useFeedsContext must be used within a FeedsProvider");
  }
  return context;
};
