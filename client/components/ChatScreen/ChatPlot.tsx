"use client";
import { ChatResponseItem } from "@/types/chat-types";
import ChartRenderer from "components/LoadChartJs/ChartRenderer";
import Image from "next/image";
import React, { useState } from "react";
import { AppModal } from "../AppModal";

interface IProps {
  chatResponse: ChatResponseItem;
  plotSettings: any;
}

const ChatPlot = ({ chatResponse, plotSettings }: IProps) => {
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [selectedImage, setSelectedImage] = useState(null);
  const onOpenModal = () => setIsModalOpen(true);
  const handleCloseModal = () => {
    setIsModalOpen(false);
    setSelectedImage("");
  };
  const handleImageClick = (imageUrl) => {
    setSelectedImage(imageUrl);
    onOpenModal();
  };

  return (
    <>
      {typeof chatResponse?.value === "string" ? (
        <div
          onClick={() => handleImageClick(chatResponse?.value)}
          className="cursor-pointer"
        >
          <Image
            src={chatResponse?.value as string}
            alt={chatResponse?.value as string}
            height="1000"
            width="1000"
            className="rounded-2xl dark:bg-white mt-4 plot-wrapper"
          />
        </div>
      ) : (
        <ChartRenderer
          chartData={plotSettings ? plotSettings : chatResponse?.value}
        />
      )}

      {isModalOpen && (
        <AppModal
          closeModal={handleCloseModal}
          modalWidth="w-[1000px]"
          isFooter={false}
        >
          <Image
            className="w-full"
            src={selectedImage}
            alt={selectedImage}
            height="1000"
            width="1000"
          />
        </AppModal>
      )}
    </>
  );
};

export default ChatPlot;
