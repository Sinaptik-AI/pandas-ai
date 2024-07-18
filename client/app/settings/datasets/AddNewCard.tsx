"use client";
import AddWorkSpaceLarge from "@/components/Icons/AddWorkSpaceLarge";
import Card from "@/components/card";
import { useAppStore } from "@/store";
import React from "react";

interface IProps {
  text: string;
}

const AddNewCard = ({ text }: IProps) => {
  const darkMode = useAppStore((state) => state.darkMode);
  return (
    <Card
      extra={"w-full py-16 px-6 h-full border dark:border-none border-[#ccc]"}
    >
      <div className="flex flex-col justify-center items-center h-full gap-6 py-[30px]">
        <AddWorkSpaceLarge color={darkMode ? "white" : "black"} />
        <h1 className="dark:text-white font-bold font-montserrat text-[15px] text-center">
          {text}
        </h1>
      </div>
    </Card>
  );
};

export default AddNewCard;
