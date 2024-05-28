"use client";
import { FetchDataframe } from "services/chatInterface";
import { ChatResponseItem } from "@/types/chat-types";
import React, { useState, useRef, useEffect } from "react";
import { FaChevronDown, FaChevronUp } from "react-icons/fa";
import { toast } from "react-toastify";
import AddPartialDialog from "./AddPartialDialog";

interface IProps {
  chatResponse: ChatResponseItem;
  index: number;
  chatId: string;
}

const StyledRecord = ({ record }: { record: string }) => {
  if (!record) return record;

  if (record === "true" || record === "True") {
    return (
      <span className="text-green-500">
        <svg
          xmlns="http://www.w3.org/2000/svg"
          className="h-4 w-4 inline"
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M5 13l4 4L19 7"
          />
        </svg>
      </span>
    );
  } else if (record === "false" || record === "False") {
    return (
      <span className="text-red-500">
        <svg
          xmlns="http://www.w3.org/2000/svg"
          className="h-4 w-4 inline"
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M6 18L18 6M6 6l12 12"
          />
        </svg>
      </span>
    );
  } else if (record.includes("http") || record.includes("www")) {
    return (
      <a
        href={record}
        target="_blank"
        rel="noreferrer noopener"
        className="text-[#86ade4] hover:underline"
      >
        {record}
      </a>
    );
  } else if (record.includes("@") && record.includes(".")) {
    return (
      <a href={`mailto:${record}`} className="text-[#86ade4] hover:underline">
        {record}
      </a>
    );
  } else {
    const dateRegex = /^\d{4}-\d{2}-\d{2}$/;
    if (dateRegex.test(record)) {
      const date = new Date(record);
      const options: Intl.DateTimeFormatOptions = {
        year: "numeric",
        month: "long",
        day: "numeric",
        hour: "numeric",
        minute: "numeric",
      };
      return date.toLocaleDateString("en-US", options);
    } else {
      return record;
    }
  }
};

const ChatDataFrame = ({ chatResponse, index, chatId }: IProps) => {
  const [openDialog, setOpenDialog] = useState(false);
  const [expandedCardId, setExpandedCardId] = useState(null);
  const [contentHeight, setContentHeight] = useState("300px");
  const [isDownloading, setIsDownloading] = useState(false);
  const contentRef = useRef(null);

  useEffect(() => {
    if (expandedCardId === index && contentRef.current) {
      setContentHeight(`${contentRef.current.scrollHeight}px`);
    } else {
      setContentHeight("300px");
    }
  }, [expandedCardId, index]);

  const handleToggleExpand = (index) => {
    setExpandedCardId((prevId) => (prevId === index ? null : index));
  };

  const handleDownload = async (id: string) => {
    setIsDownloading(true);
    await FetchDataframe(id)
      .then((response) => {
        const fileUrl = response?.data?.data?.download_url;
        const link = document.createElement("a");
        link.href = fileUrl;
        link.setAttribute("download", `dataframe-${id}`);
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
      })
      .catch((error) => {
        toast.error(
          error?.response?.data?.message
            ? error.response.data.message
            : error.message
        );
      })
      .finally(() => setIsDownloading(false));
  };

  return (
    <div className="mt-2">
      <div
        ref={contentRef}
        className={`relative bg-white dark:bg-[#333333] rounded-[20px] px-4 py-2 custom-scroll overflow-hidden overflow-x-auto transition-all`}
        style={{ maxHeight: contentHeight, height: "auto" }}
      >
        <table className="overflow-auto w-full">
          <thead>
            <tr className="!border-px !border-gray-400 uppercase p-2">
              {chatResponse?.value?.headers?.map((item, index) => (
                <th
                  key={index}
                  className="cursor-pointer border-b p-2 text-center border-solid border-r last:border-r-0 text-xs min-w-[100px]"
                >
                  {item.split("_").join(" ")}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {chatResponse?.value?.rows?.map((rows, index) => (
              <tr className="cursor-pointer" key={index}>
                {Object.values(rows).map((item, index) => (
                  <td
                    key={index}
                    className="text-center border-solid border-r dark:border-white border-[rgba(0,0,0,0.10)] last:border-r-0 pt-3"
                  >
                    <StyledRecord record={`${item}`} />
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
        {chatResponse?.value?.rows?.length > 3 && (
          <div
            className={`absolute bottom-0 left-0 right-0 h-20 bg-gradient-to-t  from-white dark:from-[#191919] to-transparent pointer-events-none ${
              expandedCardId !== index ? "opacity-100" : "opacity-0"
            } transition-all`}
          ></div>
        )}

        {expandedCardId === index && (
          <div className="text-center mt-6">
            <button
              className="cursor-pointer bg-[#191919] h-[24px] text-xs text-white font-bold rounded-full px-3 py-1"
              onClick={() => {
                handleDownload(chatId);
              }}
            >
              {isDownloading ? "Downloading..." : "Download the full table"}
            </button>
            {/* <button
              className="cursor-pointer bg-[#191919] h-[24px] text-xs text-white font-bold rounded-full px-3 py-1"
              onClick={() => setOpenDialog(true)}
            >
              Add Partials
            </button> */}
          </div>
        )}
      </div>
      <div className="text-center mt-2 flex flex-col gap-2 items-center justify-center">
        {chatResponse?.value?.rows?.length > 3 && (
          <button
            className="h-6 w-6 flex items-center justify-center text-white bg-[#191919] rounded-full"
            onClick={() => handleToggleExpand(index)}
          >
            {expandedCardId === index ? (
              <FaChevronUp size="1em" />
            ) : (
              <FaChevronDown size="1em" />
            )}
          </button>
        )}
      </div>
      {openDialog && (
        <AddPartialDialog
          chatId={chatId}
          closeDialog={() => setOpenDialog(false)}
          index={expandedCardId}
        />
      )}
    </div>
  );
};

export default ChatDataFrame;
