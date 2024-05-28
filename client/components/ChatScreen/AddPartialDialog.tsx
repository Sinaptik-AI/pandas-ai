import { AddPartialDF } from "services/chatInterface";
import { Loader } from "components/loader/Loader";
import React, { useRef, useState } from "react";
import { AiOutlineClose } from "react-icons/ai";
import { toast } from "react-toastify";

interface IProps {
  index: number;
  closeDialog: () => void;
  chatId: string;
}
const AddPartialDialog = ({ index, closeDialog, chatId }: IProps) => {
  const nameRef = useRef(null);
  const [loading, setLoading] = useState(false);
  const handleSubmit = (e) => {
    e.preventDefault();
    setLoading(true);
    const body = {
      index,
      name: nameRef.current.value,
    };
    AddPartialDF(chatId, body)
      .then((res) => {
        toast.success(res?.data?.message);
        closeDialog();
      })
      .catch((error) => {
        console.log(error);
        toast.success(
          error?.response?.data?.message
            ? error?.response.data.message
            : error.response
        );
      })
      .finally(() => setLoading(false));
  };

  return (
    <>
      <div className="fixed inset-0 z-50 flex items-center justify-center">
        <div className="md:w-[350px] sm:w-w-[320px] w-[90%] rounded  md:px-4 px-2 md:py-8 py-4  relative border  dark:text-white">
          <div className="fixed inset-0 z-50 flex items-center justify-center flex-col">
            <div
              className={
                "md:w-[350px] sm:w-w-[320px] w-[90%] rounded bg-white md:px-4 px-2 md:py-8 py-4 shadow-lg relative border dark:bg-darkMain dark:text-white"
              }
            >
              <span
                className="absolute top-2 right-2 cursor-pointer"
                onClick={() => closeDialog()}
              >
                <AiOutlineClose
                  className="text-[#191919] dark:text-white"
                  size="1.5em"
                />
              </span>
              <h4 className="my-4 md:text-xl text-md text-center">
                Add Partial DF
              </h4>
              <div className="flex justify-center gap-4 sm:pt-4">
                <form
                  className="wrap-org flex flex-col"
                  onSubmit={handleSubmit}
                >
                  <div className="input-field-org">
                    <label className="w-full">Name*</label>
                    <input
                      ref={nameRef}
                      className={`w-full p-2 border rounded dark:!bg-navy-800`}
                      type="text"
                      name="name"
                      required
                      disabled={loading}
                    />
                  </div>
                  <div className="btn-all flex justify-evenly mt-4">
                    <button
                      type="submit"
                      disabled={loading}
                      className="px-4 py-1 text-md rounded linear bg-[#191919] font-medium text-white transition duration-200 dark:bg-[#191919] dark:text-white dark:hover:bg-[#191919] dark:active:bg-[#191919]"
                    >
                      {loading ? <Loader heigth="h-6" width="w-10" /> : `Save`}
                    </button>
                  </div>
                </form>
              </div>
            </div>
          </div>
        </div>
      </div>
    </>
  );
};
export default AddPartialDialog;
