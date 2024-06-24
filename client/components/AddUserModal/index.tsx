import React, { useState } from "react";
import { AiFillDelete } from "react-icons/ai";
import Image from "next/image";
import { useAddSpaceUsers, useDeleteSpaceUsers } from "hooks/useSpaces";
import { Loader } from "components/loader/Loader";
import { toast } from "react-toastify";
import { useGetMembersList, useGetOrganizations } from "hooks/useOrganizations";
import { Input } from "../ui/input";
import AppTooltip from "../AppTooltip";

interface ISpaceUser {
  space_id: string;
  user_id: string;
  Users: {
    email: string;
    first_name: string;
    last_name: string;
  };
}

interface IProps {
  setIsModelOpen: (e) => void;
  spaceUsers: ISpaceUser[];
  spaceId: string;
}

const AddUserModal = ({ setIsModelOpen, spaceUsers, spaceId }: IProps) => {
  const [isSearchOpen, setIsSearchOpen] = useState(false);
  const [memberData, setMemberData] = useState("");
  const { data: organizationListResponse } = useGetOrganizations();
  const orgId = organizationListResponse?.data?.data[0]?.id;
  const { data: memberList } = useGetMembersList(orgId);
  const { mutateAsync: deleteSpaceUser, isPending: isDeletePending } =
    useDeleteSpaceUsers();
  const { mutateAsync: addSpaceUser, isPending: isAddPending } =
    useAddSpaceUsers();

  let unmatchedElements;
  if (spaceUsers?.length === 0) {
    unmatchedElements = memberList?.data?.data;
  } else {
    unmatchedElements = memberList?.data?.data?.filter(
      (item1) => !spaceUsers?.some((item2) => item1?.user_id === item2?.user_id)
    );
  }

  const handleDeleteSpaceUser = async (user_id) => {
    const payload = {
      user_id: user_id,
    };
    deleteSpaceUser(
      { spaceId, payload },
      {
        onSuccess(response) {
          toast.success(response?.data?.message);
          setIsModelOpen(false);
        },
        onError(error: any) {
          toast.error(
            error?.response?.data?.message
              ? error?.response?.data?.message
              : error.message
          );
          setIsModelOpen(false);
        },
      }
    );
  };
  const addUserToSpace = async (data) => {
    const payload = {
      new_member_email: data.email,
    };
    addSpaceUser(
      { spaceId, payload },
      {
        onSuccess(response) {
          toast.success(response?.data?.message);
          setIsModelOpen(false);
        },
        onError(error) {
          toast.error(error?.message);
          setIsModelOpen(false);
        },
      }
    );
  };

  return (
    <>
      <h4 className="my-4 md:text-xl text-md text-center">Add users</h4>
      {isAddPending || isDeletePending ? (
        <Loader />
      ) : (
        <div>
          <div>
            {spaceUsers?.map((user) => (
              <>
                <div key={user?.user_id} className="flex">
                  <p className="flex items-center spaces-users-list">
                    <Image
                      width="2"
                      height="20"
                      className="h-[28px] w-[28px] rounded-full cursor-pointer mr-3"
                      src="https://www.shutterstock.com/image-vector/user-profile-icon-vector-avatar-600nw-2247726673.jpg"
                      alt="Gabriele Venturi"
                    />{" "}
                    {user?.Users?.first_name} {user?.Users?.last_name}
                  </p>
                  {spaceUsers?.length === 1 ? (
                    <span
                      className="cursor-pointer min-w-[50px] border-white/0 py-3 pr-4 pl-4 flex"
                      onClick={() => handleDeleteSpaceUser(user?.user_id)}
                    >
                      <AppTooltip text="You cannot remove the sole user from this workspace">
                        <AiFillDelete
                          id="deleteIcon"
                          color="#ccc"
                          size="1.5em"
                        />
                      </AppTooltip>
                    </span>
                  ) : (
                    <span
                      className="cursor-pointer min-w-[50px] border-white/0 py-3 pr-4 pl-4 flex"
                      onClick={() => handleDeleteSpaceUser(user?.user_id)}
                    >
                      <AiFillDelete color="red" size="1.5em" />
                    </span>
                  )}
                </div>
              </>
            ))}
          </div>
          <div className="mt-3">
            <Input
              type="text"
              name="first_name"
              onClick={() => {
                setIsSearchOpen(true);
              }}
              placeholder="Search for users"
              autoComplete="off"
              onChange={(e) => {
                setMemberData(e.target.value);
              }}
            />
          </div>

          {isSearchOpen && (
            <div
              style={{
                boxShadow:
                  "rgba(60, 64, 67, 0.3) 0px 1px 2px 0px, rgba(60, 64, 67, 0.15) 0px 2px 6px 2px",
              }}
              className="mt-3 max-h-[316px] overflow-auto"
            >
              {unmatchedElements?.length > 0 &&
                unmatchedElements
                  ?.filter((Mdata) => {
                    if (memberData === "") {
                      return true;
                    } else if (
                      Mdata?.first_name
                        ?.toLowerCase()
                        ?.includes(memberData.toLowerCase())
                    ) {
                      return true;
                    }
                    return false;
                  })
                  .map((data, key) => {
                    return (
                      <p
                        key={key}
                        className="flex items-center cursor-pointer spaces_add_member mt-2 mb-2 hover:bg-[#9999] p-4"
                        onClick={() => {
                          addUserToSpace(data);
                        }}
                      >
                        <Image
                          width="2"
                          height="20"
                          className="h-[28px] w-[28px] rounded-full cursor-pointer mr-3"
                          src="https://www.shutterstock.com/image-vector/user-profile-icon-vector-avatar-600nw-2247726673.jpg"
                          alt="dummy image"
                        />{" "}
                        {data?.first_name} {data?.last_name}
                      </p>
                    );
                  })}
            </div>
          )}
        </div>
      )}
    </>
  );
};

export default AddUserModal;
