import React from "react";
import { createPortal } from "react-dom";
import { AiOutlineClose } from "react-icons/ai";
import { Button } from "../ui/button";
import { Loader } from "../loader/Loader";

interface IProps {
  closeModal?: () => void;
  handleSubmit?: () => void;
  children: React.ReactNode;
  modalWidth?: string;
  actionButtonText?: string;
  isLoading?: boolean;
  isFooter?: boolean;
}

export const AppModal = ({
  closeModal,
  children,
  modalWidth,
  handleSubmit,
  actionButtonText,
  isLoading,
  isFooter = true,
}: IProps) => {
  return (
    <>
      {createPortal(
        <div
          className="modal-container"
          onClick={(e: any) => {
            if (e.target.className === "modal-container") closeModal();
          }}
        >
          <div
            className={`rounded-[5px] relative bg-white md:px-4 px-2 md:py-8 py-4 shadow-lg border dark:bg-darkMain dark:text-white ${modalWidth}`}
          >
            <span
              className="absolute top-2 right-2 cursor-pointer"
              onClick={() => {
                closeModal();
              }}
            >
              <AiOutlineClose
                className="text-[#191919] dark:text-white"
                size="1.5em"
              />
            </span>

            <div className="mb-7 w-full">{children}</div>
            {isFooter && (
              <div className="flex items-center justify-center gap-2">
                <Button
                  type="button"
                  onClick={handleSubmit}
                  disabled={isLoading}
                >
                  {isLoading ? (
                    <Loader height="h-6" width="w-10" />
                  ) : (
                    actionButtonText
                  )}
                </Button>
                <Button
                  type="button"
                  disabled={isLoading}
                  onClick={closeModal}
                  variant="destructive"
                >
                  Cancel
                </Button>
              </div>
            )}
          </div>
        </div>,
        document.body
      )}
    </>
  );
};
