"use client";
import { useRouter } from "next/navigation";
import React, { useEffect, useState } from "react";
import { ROUTE_ADMIN } from "utils/constants";
import { useGetMe } from "@/hooks/useUsers";
import { Loader } from "@/components/loader/Loader";

const WorkSpace = () => {
  const router = useRouter();
  const [isLoading, setIsLoading] = useState(true);
  const { data: workspaceResponse } = useGetMe();
  const myDetails = workspaceResponse?.data;

  const handleSpaceClick = () => {
    localStorage.setItem("firstName", myDetails?.first_name);
    localStorage.setItem("email", myDetails?.email);
    localStorage.setItem("user_id", myDetails?.id);
    localStorage.setItem(
      "selectedOrganization",
      JSON.stringify(myDetails?.organizations[0])
    );
    localStorage.setItem("spaceId", myDetails?.space?.id);
    localStorage.setItem("spaceName", myDetails?.space?.name);
    router.push(ROUTE_ADMIN);
    setIsLoading(false);
  };

  useEffect(() => {
    if (workspaceResponse?.data) {
      handleSpaceClick();
    }
  }, [workspaceResponse]);

  return (
    <>
      {isLoading && (
        <div className="flex items-center justify-center m-auto h-full w-full">
          <Loader />
        </div>
      )}
    </>
  );
};

export default WorkSpace;
