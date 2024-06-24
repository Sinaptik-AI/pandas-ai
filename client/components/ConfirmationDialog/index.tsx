"use client";
import { AppModal } from "components/AppModal";
import React from "react";

interface IProps {
  text: string;
  onCancel?: () => void;
  onSubmit?: () => void;
  isLoading?: boolean;
  actionButtonText?: string;
}

const ConfirmationDialog = ({
  text,
  onCancel,
  onSubmit,
  isLoading,
  actionButtonText = "Yes",
}: IProps) => {
  return (
    <AppModal
      closeModal={onCancel}
      actionButtonText={actionButtonText}
      handleSubmit={onSubmit}
      isLoading={isLoading}
      modalWidth="w-[350px]"
    >
      <h4 className="my-4 sm:text-sm md:text-lg text-center">{text}</h4>
    </AppModal>
  );
};

export default ConfirmationDialog;
