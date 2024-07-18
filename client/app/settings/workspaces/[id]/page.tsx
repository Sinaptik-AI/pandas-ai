import React from "react";
import Card from "components/card";

import { GetWorkspaceDetails } from "@/services/spaces";
import Link from "next/link";
import { Button } from "@/components/ui/button";
import AddNewCard from "../../datasets/AddNewCard";
import { FaFileCsv } from "react-icons/fa";
import WorkspaceCard from "./WorkspaceCard";

interface PageProps {
  params: {
    id: string;
  };
}

export default async function WorkSpacesDetails({ params }: PageProps) {
  const data = await GetWorkspaceDetails(params.id);

  return (
    <div className="w-full h-full overflow-y-auto custom-scroll mt-5 px-2 md:px-4">
      <h1 className="text-2xl font-bold dark:text-white mb-10">
        <Link href="/settings/workspaces">Workspaces</Link>
        <small>{data?.name && ` › ${data?.name}`}</small>
      </h1>

      <div className="flex flex-col p-2 md:p-4 font-montserrat">
        <div className="flex items-center md:flex-row flex-col justify-center gap-4">
          <WorkspaceCard data={data} />
          <Card extra={"w-full py-4 px-6 h-full mb-4"}>
            <div className="flex flex-col justify-between min-h-[300px]">
              <div>
                <h3 className="font-bold text-[20px] mb-1">People</h3>
                <div className="flex flex-col mt-2">
                  <span>{data?.name}</span>
                </div>
              </div>
            </div>
          </Card>
        </div>

        <h1 className="text-neutral-500 mt-6 text-xl font-bold dark:text-white">
          Datasets
        </h1>
        <div className="mt-2 grid h-full gap-5 grid-cols-1 md:grid-cols-2 xl:grid-cols-3 2xl:grid-cols-4">
          {data?.dataset_spaces?.map((df) => (
            <Card
              key={df.dataset_id}
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
                    <h1 className="dark:text-white font-bold font-montserrat text-[20px] text-center customellipsis">
                      {df?.dataset?.name}
                    </h1>
                  </div>
                </div>
              </header>
              <div className="w-full flex flex-wrap items-center justify-center mt-1">
                <Link href={`/settings/datasets/${df?.dataset?.id}`}>
                  <Button>Details</Button>
                </Link>
              </div>
            </Card>
          ))}
          <Link href={`/settings/datasets/add?space_id=${params.id}`}>
            <AddNewCard text="New dataset" />
          </Link>
        </div>
      </div>
    </div>
  );
}
