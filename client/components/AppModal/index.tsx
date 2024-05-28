import React from "react";
import { createPortal } from "react-dom";
import FormButton from "components/Buttons/FormButton";
import { AiOutlineClose } from "react-icons/ai";

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

            <div className="mb-5 w-full">{children}</div>
            {isFooter && (
              <div className="flex items-center justify-center gap-2">
                <FormButton
                  text={actionButtonText}
                  type="button"
                  onClick={handleSubmit}
                  isLoading={isLoading}
                  disabled={isLoading}
                />
                <button
                  type="button"
                  disabled={isLoading}
                  onClick={closeModal}
                  className={`px-6 py-1 border rounded-[10px] border-[#D30000] flex flex-wrap items-center justify-center cursor-pointer bg-[#D30000] font-bold text-white font-montserrat`}
                >
                  Cancel
                </button>
              </div>
            )}
          </div>
        </div>,
        document.body,
      )}
    </>
  );
};
