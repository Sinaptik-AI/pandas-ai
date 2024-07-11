"use client";
import React, { useState } from "react";
import Card from "@/components/card";
import LogsTable from "components/LogsTable/index";
import { LogData } from "./logs-interface";
import Pagination from "@/components/pagination";

interface IProps {
  logs: LogData[];
  logs_count: number;
}

const LogsCard = ({ logs, logs_count }: IProps) => {
  const [page, setPage] = useState(1);
  const itemsPerPage = 15;

  const totalPages = Math.ceil(logs_count / itemsPerPage);
  return (
    <Card extra="w-full py-2 px-5">
      <LogsTable data={logs} />
      <div className="flex justify-end float-right m-4">
        <div>
          {totalPages > 1 && (
            <Pagination page={page} setPage={setPage} totalPages={totalPages} />
          )}
        </div>
      </div>
    </Card>
  );
};

export default LogsCard;
