import React from "react";
import Skeleton, { SkeletonTheme } from "react-loading-skeleton";
import "react-loading-skeleton/dist/skeleton.css";
import { useAppStore } from "store";
import Card from "../card";

export const WorkSpaceLoader = () => {
  const darkMode = useAppStore((state) => state.darkMode);
  return (
    <SkeletonTheme
      baseColor={darkMode && "#191919"}
      highlightColor={darkMode && "#333333"}
    >
      <Skeleton width={140} height={35} count={4} inline className="mr-4" />
    </SkeletonTheme>
  );
};

export const ConversationsHistoryLoader = ({
  amount = 3,
}: {
  amount?: number;
}) => {
  const darkMode = useAppStore((state) => state.darkMode);
  return (
    <div className="w-full px-4">
      <SkeletonTheme
        baseColor={darkMode && "#191919"}
        highlightColor={darkMode && "#333333"}
      >
        <Skeleton height={25} width={90} />
        <Skeleton height={25} count={5} />
        {Array.from({ length: amount - 1 }, (_, index) => (
          <React.Fragment key={index}>
            <Skeleton height={25} width={90} className="mt-5" />
            <Skeleton height={25} count={5} />
          </React.Fragment>
        ))}
      </SkeletonTheme>
    </div>
  );
};

export const RightSidebarLoader = () => {
  const darkMode = useAppStore((state) => state.darkMode);
  return (
    <div className="w-full">
      <SkeletonTheme
        baseColor={darkMode && "#191919"}
        highlightColor={darkMode && "#333333"}
      >
        <Skeleton height={25} width={90} />
        <Skeleton height={25} count={3} className="w-full" />
      </SkeletonTheme>
    </div>
  );
};

export const GetChatLabelLoader = () => {
  const darkMode = useAppStore((state) => state.darkMode);
  return (
    <SkeletonTheme
      baseColor={darkMode && "#191919"}
      highlightColor={darkMode && "#333333"}
    >
      <Skeleton width={90} />
    </SkeletonTheme>
  );
};

export const ChatReactionLoader = () => {
  const darkMode = useAppStore((state) => state.darkMode);
  return (
    <SkeletonTheme
      baseColor={darkMode && "#191919"}
      highlightColor={darkMode && "#333333"}
    >
      <Skeleton width={250} />
      <Skeleton width={190} />
      <Skeleton width={270} />
    </SkeletonTheme>
  );
};

export const SingleChatMessageLoader = () => {
  const darkMode = useAppStore((state) => state.darkMode);
  return (
    <SkeletonTheme
      baseColor={darkMode && "#191919"}
      highlightColor={darkMode && "#333333"}
    >
      <div className="ml-14">
        <Skeleton width={90} className="mb-2" />
        <Skeleton width={250} />
        <Skeleton width={190} />
        <Skeleton width={270} />
      </div>
    </SkeletonTheme>
  );
};

export const ChatPlaceholderLoader = () => {
  const darkMode = useAppStore((state) => state.darkMode);
  return (
    <SkeletonTheme
      baseColor={darkMode && "#191919"}
      highlightColor={darkMode && "#333333"}
    >
      <div>
        <div className="border-b-[#333333] border-b pb-5">
          <SingleChatMessageLoader />
        </div>
        <div className="border-b-[#333333] border-b py-5">
          <SingleChatMessageLoader />
        </div>
        <div className="py-5">
          <SingleChatMessageLoader />
        </div>
      </div>
    </SkeletonTheme>
  );
};

export const ExplainMessageLoader = () => {
  const darkMode = useAppStore((state) => state.darkMode);
  return (
    <SkeletonTheme
      baseColor={darkMode && "#191919"}
      highlightColor={darkMode && "#333333"}
    >
      <Skeleton width={90} className="mb-2" />
      <Skeleton />
      <Skeleton />
      <Skeleton />
    </SkeletonTheme>
  );
};
export const DatasetCardLoading = () => {
  const darkMode = useAppStore((state) => state.darkMode);
  return (
    <SkeletonTheme
      baseColor={darkMode && "#191919"}
      highlightColor={darkMode && "#333333"}
    >
      <Card extra={"w-full py-4 px-6 h-full mb-4"}>
        <div className="flex flex-col justify-between h-[170px]">
          <div>
            <Skeleton width={200} className="mb-1" />

            <h3 className="font-bold text-sm mb-1">
              <Skeleton width={200} className="mb-2" />
            </h3>
          </div>
          <div className="flex justify-start gap-4 items-center flex-wrap">
            <Skeleton width={290} />
          </div>
        </div>
      </Card>
    </SkeletonTheme>
  );
};
