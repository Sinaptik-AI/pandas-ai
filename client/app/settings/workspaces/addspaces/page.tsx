import React from "react";
import Link from "next/link";
import { GetAllDataSets } from "@/services/datasets";
import AddSpaceCard from "./AddSpaceCard";
import { Button } from "@/components/ui/button";

export const dynamic = 'force-dynamic';

export default async function AddSpaces() {
  const data = await GetAllDataSets();

  return (
    <div className="w-full h-full overflow-y-auto custom-scroll mt-5 px-2 md:px-4">
      <h1 className="text-2xl font-bold dark:text-white mb-10">
        <Link href="/settings/workspaces">Workspaces</Link>
        <small> › New</small>
      </h1>

      {data?.datasets?.length === 0 ? (
        <div className="flex flex-col items-center justify-center m-auto">
          <p className="dark:text-white font-montserrat text-lg mb-3">
            No datasets available, please add one
          </p>

          <Link href={"/settings/datasets/add"}></Link>
          <Button>Add</Button>
        </div>
      ) : (
        <AddSpaceCard datasets={data?.datasets} />
      )}
    </div>
  );
}
