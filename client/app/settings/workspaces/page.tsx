import React from "react";
import Card from "components/card";
import Link from "next/link";
import AddNewCard from "../datasets/AddNewCard";
import AppTooltip from "@/components/AppTooltip";
import { Button } from "@/components/ui/button";
import { GetAllWorkspaces } from "@/services/spaces";

export const dynamic = 'force-dynamic';

export default async function WorkSpaces() {
  const data = await GetAllWorkspaces();

  return (
    <div className="w-full overflow-y-auto custom-scroll px-2 mt-5 md:px-4 h-full">
      <h1 className="text-2xl font-bold dark:text-white mb-10">Workspaces</h1>

      <div className="grid 2xl:grid-cols-4 xl:grid-cols-3 lg:grid-cols-2 gap-4">
        {data?.map((item, index) => (
          <Card
            key={index}
            extra={
              "w-full py-4 px-6 h-full border dark:border-none border-[#ccc]"
            }
          >
            <div className="flex flex-col justify-center items-center gap-6 py-[30px]">
              <div className="h-[65px] w-full overflow-hidden">
                <AppTooltip text={item.name}>
                  <h1
                    data-tooltip-id={item.id}
                    className="dark:text-white font-bold font-montserrat text-[20px] text-center customellipsis"
                  >
                    {item.name}
                  </h1>
                </AppTooltip>
              </div>

              <div className="w-full flex flex-wrap items-center justify-center mt-1">
                <Link href={`/settings/workspaces/${item?.id}`}>
                  <Button>Details</Button>
                </Link>
              </div>
            </div>
          </Card>
        ))}
        <Link href={"/settings/workspaces/addspaces"}>
          <AddNewCard text="New workspace" />
        </Link>
      </div>
    </div>
  );
}


