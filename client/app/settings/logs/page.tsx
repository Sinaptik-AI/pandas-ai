"use client";
import React, { useState } from "react";
import { Loader } from "components/loader/Loader";
import Pagination from "../../../components/pagination/index";
import Card from "components/card";
import LogsTable from "components/LogsTable/index";
import { useGetLogs } from "@/hooks/useLogs";

const Logs: React.FC = () => {
  const { data: logsResponse, isLoading } = useGetLogs();
  const itemsPerPage = 15;
  const [page, setPage] = useState(1);

  const totalPages = Math.ceil(logsResponse?.data?.logs_count / itemsPerPage);

  return (
    <div className="w-full h-full overflow-y-auto custom-scroll mt-5 px-2 md:px-4">
      <h1 className="text-2xl font-bold dark:text-white mb-10">Logs</h1>
      {isLoading ? (
        <Loader />
      ) : (
        <Card extra="w-full py-2 px-5">
          <>
            <LogsTable data={logsResponse?.data?.logs} />
          </>
          <div className="flex justify-end float-right m-4">
            <div>
              {totalPages > 1 && (
                <Pagination
                  page={page}
                  setPage={setPage}
                  totalPages={totalPages}
                />
              )}
            </div>
          </div>
        </Card>
      )}
    </div>
  );
};
export default Logs;
