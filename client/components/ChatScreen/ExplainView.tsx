import React from "react";
import { IoMdClose } from "react-icons/io";
import { useExplainConversationMessage } from "hooks/useConversations";
import { useAppStore } from "store";
import { ExplainMessageLoader } from "components/Skeletons";

interface IProps {
  closeEditor: () => void;
}

const ExplainView = ({ closeEditor }: IProps) => {
  const selectedChatItem = useAppStore((state) => state.selectedChatItem);
  const { data: explainData, isLoading } = useExplainConversationMessage(
    selectedChatItem?.conversation_id,
    selectedChatItem?.id,
  );

  return (
    <div className="relative flex flex-col justify-center items-center rounded-[20px] bg-[#191919]">
      <div
        className="absolute right-2 top-2 cursor-pointer"
        onClick={closeEditor}
      >
        <IoMdClose color={"white"} size="1.2rem" />
      </div>

      {isLoading ? (
        <div className="text_editabel pt-5 w-full h-full p-4 md:p-6">
          <ExplainMessageLoader />
        </div>
      ) : (
        <div className="text_editabel pt-5 w-full h-full p-4 md:p-6">
          <p className="dark:text-white">
            {explainData?.data?.data?.explanation}
          </p>
        </div>
      )}
    </div>
  );
};

export default ExplainView;
