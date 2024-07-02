import React from "react";
import { MdCheckCircle, MdAvTimer, MdCancel } from "react-icons/md";
import Card from "components/card";
import CodeHighlight from "components/codeHighlight/codeHighlight";
import Image from "next/image";
import { isBase64Image } from "utils/base64";
import { FormatDate } from "utils/formatDate";
import { LogsDetailInterface } from "../logs-interface";
import ExecutionDetails from "components/ExecutionDetails";
import Link from "next/link";
import RenderDataFrame from "./RenderDataFrame";
import ChartRenderer from "components/LoadChartJs/ChartRenderer";
import { GetLogDetails } from "@/services/logs";

const FormattedOutput = ({ data }: { data: any }) => {
  const inputData = Array.isArray(data?.data?.value)
    ? data?.data?.value
    : [data?.data?.value];

  return inputData.map((value: any, index: number) => (
    <div key={index} className="mt-5">
      {isBase64Image(value?.value) && (
        <Image
          src={`${value?.value}`}
          alt={"No Image"}
          height="700"
          width="700"
        />
      )}
      {value?.type == "plot" && (
        <ChartRenderer chartData={value?.value} key={index} />
      )}
      {value?.type == "dataframe" && (
        <RenderDataFrame table={value?.value} index={index} />
      )}
      {value?.type == "string" && value?.value}
      {value?.type == "number" && value?.value}
    </div>
  ));
};

export default async function LogDetails({
  params,
}: {
  params: { id: string };
}) {
  const data = await GetLogDetails(params.id);
  const logsDetail: LogsDetailInterface = data?.log?.json_log;

  return (
    <div className="w-full h-full overflow-y-auto custom-scroll mt-5 px-2 md:px-4">
      <h1 className="text-2xl font-bold dark:text-white mb-10">
        <Link href="/settings/logs">Logs</Link>
        <small>
          {logsDetail?.query_info?.query &&
            ` › ${logsDetail?.query_info?.query}`}
        </small>
      </h1>
      {!logsDetail ? (
        <div className="dark:text-white mt-4">No logs available</div>
      ) : (
        <div>
          <div className="min-h-sceen max-w-screen mx-auto bg-white px-3 dark:bg-[#0b14374d] dark:text-white">
            <div className="items-left flex flex-col ">
              <p className="text-md mt-2   text-base font-normal">
                {logsDetail?.response?.type == "plot" &&
                  !isBase64Image(logsDetail?.response?.value) && (
                    <p>
                      {typeof logsDetail?.response?.value === "string" &&
                        logsDetail?.response?.value}
                    </p>
                  )}
              </p>
              <ExecutionDetails
                executionTime={`${parseFloat(
                  String(logsDetail?.execution_time)
                ).toFixed(2)} s`}
                executionDate={FormatDate(data?.log?.created_at)}
                instance={logsDetail?.query_info?.instance}
                user={"PandasAI"}
              />
            </div>
            <div className="mx-auto mt-8 grid w-full divide-y">
              <div className="py-5">
                {/* ///// DataFrames Card */}
                <details
                  className="group"
                  style={
                    logsDetail?.dataframes?.length > 0
                      ? { pointerEvents: "all" }
                      : { pointerEvents: "none" }
                  }
                >
                  <summary className="flex cursor-pointer list-none items-center justify-between font-medium">
                    <span>Input Datasets</span>
                    <div className="wrapper_status_arrow flex">
                      <span className="transition group-open:rotate-180">
                        <svg
                          fill="none"
                          height="24"
                          shapeRendering="geometricPrecision"
                          stroke="currentColor"
                          strokeLinecap="round"
                          strokeLinejoin="round"
                          strokeWidth="1.5"
                          viewBox="0 0 24 24"
                          width="24"
                        >
                          <path d="M6 9l6 6 6-6"></path>
                        </svg>
                      </span>
                    </div>
                  </summary>
                  <div className="mt-5 h-full">
                    <div>
                      <div className={`mt-5 grid h-full gap-5`}>
                        {logsDetail?.dataframes?.map((table, index) => (
                          <RenderDataFrame
                            key={index}
                            table={table}
                            index={index}
                          />
                        ))}
                      </div>
                    </div>
                  </div>
                </details>
              </div>
              {logsDetail?.steps?.map((data, key) => {
                return (
                  <div className="py-5" key={key}>
                    <details
                      className="group"
                      style={
                        data?.code_generated ||
                        data?.generated_prompt ||
                        data?.message ||
                        data?.result?.value
                          ? { pointerEvents: "all" }
                          : { pointerEvents: "none" }
                      }
                    >
                      <summary className="flex cursor-pointer list-none items-center justify-between font-medium">
                        <span> {data?.type}</span>
                        <div
                          className="wrapper_status_arrow flex"
                          style={
                            data?.code_generated ||
                            data?.generated_prompt ||
                            data?.message ||
                            data?.result?.value
                              ? {}
                              : { marginRight: "1.4rem" }
                          }
                        >
                          <div className="time_status mr-4 flex items-center justify-center sm:mr-12">
                            <span>
                              {!Number.isNaN(
                                Math?.round(data?.execution_time)
                              ) && (
                                <MdAvTimer className="mr-1 inline-block text-gray-400" />
                              )}
                              {!Number.isNaN(
                                Math?.round(data?.execution_time)
                              ) &&
                                (
                                  Math?.round(data?.execution_time * 100) / 100
                                ).toFixed(2)}
                            </span>
                            <span style={{ marginLeft: "1rem" }}>
                              {data?.success ? (
                                <MdCheckCircle className="me-1 text-green-500 dark:text-green-300" />
                              ) : (
                                <MdCancel className="me-1 text-red-500 dark:text-red-300" />
                              )}
                            </span>
                          </div>
                          {data?.code_generated ||
                          data?.generated_prompt ||
                          data?.message ||
                          data?.result?.value ? (
                            <span className="transition group-open:rotate-180">
                              <svg
                                fill="none"
                                height="24"
                                shapeRendering="geometricPrecision"
                                stroke="currentColor"
                                strokeLinecap="round"
                                strokeLinejoin="round"
                                strokeWidth="1.5"
                                viewBox="0 0 24 24"
                                width="24"
                              >
                                <path d="M6 9l6 6 6-6"></path>
                              </svg>
                            </span>
                          ) : (
                            <span className="hidden transition group-open:rotate-180">
                              <svg
                                fill="none"
                                height="24"
                                shapeRendering="geometricPrecision"
                                stroke="currentColor"
                                strokeLinecap="round"
                                strokeLinejoin="round"
                                strokeWidth="1.5"
                                viewBox="0 0 24 24"
                                width="24"
                              >
                                <path d="M6 9l6 6 6-6"></path>
                              </svg>
                            </span>
                          )}
                        </div>
                      </summary>
                      <code className="text-neutral-600 group-open:animate-fadeIn mt-3">
                        <>
                          <Card
                            extra={
                              "w-full h-full sm:overflow-auto sm:px-6 px-0 py-5 mt-3"
                            }
                          >
                            <p className="mb-2">
                              {data?.generated_prompt || data?.message}
                            </p>
                            {data?.data?.content_type == "code" ||
                            data?.data?.content_type == "prompt" ? (
                              <CodeHighlight
                                code={data?.data?.value as string}
                                codeExecution={data?.data?.content_type}
                              />
                            ) : (
                              ""
                            )}

                            {data?.data?.exception && (
                              <>
                                <p className="mt-5 mb-2">An error occurred</p>
                                <CodeHighlight
                                  code={data?.data?.exception as string}
                                  codeExecution={data?.data?.content_type}
                                />
                              </>
                            )}
                            {data?.type == "CodeExecution" &&
                              data?.data?.content_type == "response" && (
                                <>
                                  <hr />
                                  <FormattedOutput data={data} />
                                </>
                              )}
                          </Card>
                        </>
                      </code>
                    </details>
                  </div>
                );
              })}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
