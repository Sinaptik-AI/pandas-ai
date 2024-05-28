"use client";
import { WorkSpaceLoader } from "components/Skeletons";
import ToggleDarkModeComponent from "components/ToggleDarkMode";
import { useGetAllSpaces } from "hooks/useSpaces";
import { useRouter } from "next/navigation";
import React from "react";
import { ROUTE_ADMIN } from "utils/constants";
import WorkSpaceHeader from "../../components/WorkSpace/header";
import {
  FETCH_CONVERSATION,
  useConversationsContext,
} from "contexts/ConversationsProvider";
import Link from "next/link";

const WorkSpace = () => {
  const firstName = localStorage.getItem("firstName") || null;
  const router = useRouter();
  const storeContext = useConversationsContext();

  const { data: workspaceResponse, isLoading } = useGetAllSpaces();
  const handleSpaceClick = (e, space) => {
    e.preventDefault();
    localStorage.setItem("spaceId", space.id);
    localStorage.setItem("spaceName", space.name);
    storeContext.dispatch({
      type: FETCH_CONVERSATION,
      payload: [],
    });
    router.push(ROUTE_ADMIN);
  };

  return (
    <div className={`flex flex-col dark:bg-black bg-white min-h-screen`}>
      <div>
        <WorkSpaceHeader />
      </div>
      <div className="flex flex-col justify-center items-center w-full h-[75vh]">
        <div className="text-center mx-auto w-full md:w-[700px]">
          <h5
            className={`text-[18px] md:text-[30px] font-medium mb-[14px] dark:text-white leading-10`}
          >
            Hey {!firstName ? "" : ` ${firstName} 👋,`}
            <br />
            select your workspace
          </h5>
          {isLoading ? (
            <WorkSpaceLoader />
          ) : (
            <div className="flex flex-wrap items-center justify-center gap-4 mt-5">
              {workspaceResponse?.data?.data?.spaces?.map((space) => (
                <Link
                  href={ROUTE_ADMIN}
                  key={space.id}
                  className="h-[37px] min-w-[136px] px-2 border rounded-[10px] flex flex-wrap items-center justify-center cursor-pointer dark:bg-white neon-on-hover"
                  onClick={(e) => handleSpaceClick(e, space)}
                >
                  <span className="font-semibold text-black">{space.name}</span>
                </Link>
              ))}
            </div>
          )}
        </div>
      </div>
      <div className="md:absolute absolute bottom-5 left-10 flex">
        <ToggleDarkModeComponent />
      </div>
    </div>
  );
};

export default WorkSpace;
