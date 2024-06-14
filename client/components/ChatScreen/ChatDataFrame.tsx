"use client";
import { ChatResponseItem } from "@/types/chat-types";
import React, { useState, useRef, useEffect } from "react";
import { Grid } from "gridjs";
import DownloadIcon from "../Icons/DownloadIcon";
import SearchIcon from "../Icons/SearchIcon";
import { useAppStore } from "@/store";
import AppTooltip from "../AppTooltip";
import { convertToCSV } from "@/utils/convertToCSV";
import "gridjs/dist/theme/mermaid.css";

interface IProps {
  chatResponse: ChatResponseItem;
  chatId: string;
}

const ChatDataFrame = ({ chatResponse, chatId }: IProps) => {
  const contentRef = useRef(null);
  const [search, setSearch] = useState(false);
  const darkMode = useAppStore((state) => state.darkMode);

  const grid = new Grid({
    columns: chatResponse?.value?.headers,
    data: chatResponse?.value?.rows,
    sort: true,
    search: true,
    pagination: {
      limit: 10,
      summary: false,
    },
    style: {
      table: {
        "white-space": "nowrap",
      },
    },
    height: "600px",
    resizable: true,
  });

  useEffect(() => {
    grid.render(contentRef.current);
  });

  const handleSearch = () => {
    const gridJsHead = contentRef.current.querySelector(".gridjs-head");

    if (gridJsHead) {
      gridJsHead.style.display = search ? "none" : "block";
      setSearch(!search);
    }
  };

  const handleDownload = async () => {
    const { headers, rows } = chatResponse.value;
    const csvData = convertToCSV(headers, rows);
    const blob = new Blob([csvData], { type: "text/csv" });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.setAttribute("href", url);
    a.setAttribute("download", `dataframe-${chatId}.csv`);
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    window.URL.revokeObjectURL(url);
  };

  return (
    <div className="flex flex-col mt-2">
      <div className="flex justify-end">
        <div className="cursor-pointer" onClick={handleSearch}>
          <AppTooltip text="Search">
            <SearchIcon color={darkMode ? "#fff" : "#000"} />
          </AppTooltip>
        </div>
        <div className="cursor-pointer" onClick={handleDownload}>
          <AppTooltip text="Download">
            <DownloadIcon color={darkMode ? "#fff" : "#000"} />
          </AppTooltip>
        </div>
      </div>
      <div ref={contentRef} className={`grid-container${chatId}`} />
    </div>
  );
};

export default ChatDataFrame;
