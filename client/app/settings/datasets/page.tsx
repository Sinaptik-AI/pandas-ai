"use client";
import React from "react";
import { Loader } from "components/loader/Loader";
import Link from "next/link";
import AddWorkSpaceLarge from "components/Icons/AddWorkSpaceLarge";
import { useAppStore } from "store";
import Card from "@/components/card";
import { useGetAllDataSets } from "@/hooks/useDatasets";
import AppTooltip from "@/components/AppTooltip";
import { FaFileCsv } from "react-icons/fa";
import { Button } from "@/components/ui/button";

const Datasets = () => {
  const darkMode = useAppStore((state) => state.darkMode);
  const { data: datasetsResponse, isLoading } = useGetAllDataSets();

  return (
    <div className="w-full h-full overflow-y-auto custom-scroll mt-5 px-2 md:px-4">
      <h1 className="text-2xl font-bold dark:text-white mb-10">Datasets</h1>
      {isLoading ? (
        <Loader />
      ) : (
        <>
          <div className="grid 2xl:grid-cols-4 xl:grid-cols-3 lg:grid-cols-2 gap-4">
            {datasetsResponse?.data?.datasets?.map((item) => (
              <Card
                key={item.id}
                extra={
                  "w-full pt-4 px-6 h-full border dark:border-none border-[#ccc] pb-8"
                }
              >
                <header className="relative flex items-center justify-between">
                  <div className="w-full">
                    <div className="flex justify-center h-24">
                      <FaFileCsv size="4em" key={0} />
                    </div>
                    <div className="h-[65px] w-full overflow-hidden">
                      <AppTooltip text={item.name}>
                        <h1
                          data-tooltip-id={`${item.id}`}
                          className="dark:text-white font-bold font-montserrat text-[20px] text-center customellipsis"
                        >
                          {item.name}
                        </h1>
                      </AppTooltip>
                    </div>
                  </div>
                </header>
                <div className="w-full flex flex-wrap items-center justify-center mt-1">
                  <Link href={`/settings/datasets/${item?.id}`}>
                    <Button>Details</Button>
                  </Link>
                </div>
              </Card>
            ))}

            <Link href={`/settings/datasets/add`}>
              <Card
                extra={
                  "w-full py-16 px-6 h-full border dark:border-none border-[#ccc]"
                }
              >
                <div className="flex flex-col justify-center items-center h-full gap-6 py-[30px]">
                  <AddWorkSpaceLarge color={darkMode ? "white" : "black"} />
                  <h1 className="dark:text-white font-bold font-montserrat text-[15px] text-center">
                    New dataset
                  </h1>
                </div>
              </Card>
            </Link>
          </div>
        </>
      )}
    </div>
  );
};

export default Datasets;
