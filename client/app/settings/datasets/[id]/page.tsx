import React from "react";
import Link from "next/link";
import DatasetCard from "./DatasetCard";
import { GetDatasetDetails } from "@/services/datasets";

interface PageProps {
  params: {
    id: string;
  };
}

export default async function DatasetDetailsPage({ params }: PageProps) {
  const data = await GetDatasetDetails(params.id);
  const dataframe = data?.dataset;

  return (
    <>
      <div className="w-full h-full overflow-y-auto custom-scroll mt-5 px-2 md:px-4">
        <h1 className="text-2xl font-bold dark:text-white mb-10">
          <Link href="/settings/datasets">Datasets</Link>
          <small>{` › ${dataframe?.name || ""}`}</small>
        </h1>

        <div className="flex flex-col p-2 md:p-4 font-montserrat">
          <div className="flex items-center justify-center w-[50%]">
            <DatasetCard dataframe={dataframe} />
          </div>
        </div>
      </div>
    </>
  );
}
export const dynamic='force-dynamic';

