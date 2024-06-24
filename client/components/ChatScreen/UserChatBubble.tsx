import Image from "next/image";
import React from "react";

interface IProps {
  query: string;
}

const UserChatBubble = ({ query }: IProps) => {
  return (
    <div className="border-b-[#333333] border-b pb-5">
      <div className="flex w-full font-montserrat gap-4">
        <div className="flex h-7 w-7 md:h-10 md:w-10 rounded-full overflow-hidden bg-[#191919] flex-shrink-0">
          <Image
            src="https://www.shutterstock.com/image-vector/user-profile-icon-vector-avatar-600nw-2247726673.jpg"
            alt="logo"
            width="2"
            height="20"
            className="h-7 w-7 md:h-10 md:w-10  rounded-full"
          />
        </div>
        <div className="flex flex-col">
          <span className="dark:text-white font-bold text-lg">You</span>
          <div className="font-medium">
            <p className="text-lg dark:text-white font-normal">{query}</p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default UserChatBubble;
