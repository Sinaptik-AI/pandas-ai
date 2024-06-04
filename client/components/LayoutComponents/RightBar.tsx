"use client";
import { useGetSpaceUsers } from "hooks/useSpaces";
import React, { useState } from "react";
import { useAppStore } from "store";
import AddWorkSpace from "components/Icons/AddWorkSpace";
import { RightSidebarLoader } from "components/Skeletons";
import AddUserModal from "components/AddUserModal";
import { AppModal } from "components/AppModal";

const RightBar = () => {
  const darkMode = useAppStore((state) => state.darkMode);
  const spaceId = localStorage.getItem("spaceId");
  const isAdmin = localStorage.getItem("is_admin");
  const [isModalOpen, setIsModalOpen] = useState(false);

  const { data: usersResponse, isLoading: isGetSpaceUserLoading } =
    useGetSpaceUsers(spaceId);

  return (
    <>
      <div
        className={`w-[350px] h-full flex flex-col font-montserrat dark:bg-black bg-white`}
      >
        <div className="mt-5 w-full flex-1 overflow-y-auto custom-scroll flex justify-center dark:text-white font-montserrat">
          <div className="flex-1 px-5">
            {isGetSpaceUserLoading ? (
              <div className="w-full flex-1 mt-12">
                <RightSidebarLoader />
              </div>
            ) : (
              <div>
                <h2 className={`font-semibold text-2xl dark:text-white mt-12`}>
                  Team
                </h2>
                <div className="pt-1">
                  {usersResponse?.data?.data?.map((user) => (
                    <p className="pt-[2px] font-light" key={user.user_id}>
                      {user?.Users?.first_name}
                    </p>
                  ))}
                  {isAdmin && (
                    <div
                      onClick={() => setIsModalOpen(true)}
                      className="max-w-[50px] p-2 dark:border-[#262626] border rounded-[10px] flex items-center justify-center mt-2 cursor-pointer dark:bg-[#262626]"
                    >
                      <AddWorkSpace
                        color={darkMode ? "white" : "black"}
                        size={12}
                      />
                    </div>
                  )}
                </div>
              </div>
            )}
          </div>
        </div>
      </div>

      {isModalOpen && (
        <AppModal
          closeModal={() => setIsModalOpen(false)}
          modalWidth="w-[350px]"
          isFooter={false}
        >
          <AddUserModal
            setIsModelOpen={() => setIsModalOpen(false)}
            spaceUsers={usersResponse?.data?.data}
            spaceId={spaceId}
          />
        </AppModal>
      )}
    </>
  );
};

export default RightBar;
