"use client";
import React, { useState } from "react";
import { Loader } from "components/loader/Loader";
import Multiselect from "multiselect-react-dropdown";
import { useRouter } from "next/navigation";
import { toast } from "react-toastify";
import { AddWorkspace } from "@/services/spaces";
import { revalidateWorkspaces } from "@/lib/actions";

interface IProps {
  datasets: any;
}

interface DataFrame {
  id: number;
  name: string;
}
const AddSpaceCard = ({ datasets }: IProps) => {
  const [name, setName] = useState<string>("");
  const [items, setItems] = useState<DataFrame[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [nameError, setNameError] = useState<string>("");
  const [dataFramesError, setDataFramesError] = useState<string>("");
  const dataFrameNames = [];
  const dataFrameIds: number[] = [];
  const router = useRouter();

  items.forEach((data) => {
    return dataFrameIds?.push(data.id);
  });

  datasets?.map((data) => {
    return dataFrameNames.push({ id: data?.id, name: data?.name });
  });

  const handleSelect = (selectedList) => {
    setItems(selectedList);
  };

  const handleSelectRemove = (selectedList) => {
    setItems(selectedList);
  };

  const handleSubmit = async () => {
    setNameError("");
    let isValid = true;
    if (name?.trim() === "") {
      setNameError("Name field is required");
      isValid = false;
    }

    if (items?.length === 0) {
      setDataFramesError("Tables is required");
      isValid = false;
    }

    if (!isValid) {
      return;
    }
    setIsLoading(true);
    const payLoad = {
      name: name,
      datasets: [...dataFrameIds],
    };
    await AddWorkspace(payLoad)
      .then((response) => {
        toast.success(response?.data?.message);
        setName("");
        revalidateWorkspaces();
        router.push("/settings/workspaces");
      })
      .catch((error) => {
        toast.error(
          error?.response?.data?.message
            ? error?.response?.data?.message
            : error?.message
        );
      })
      .finally(() => setIsLoading(false));
  };

  return (
    <div className="!z-5 mx-auto relative rounded-[20px] bg-white bg-clip-border shadow-3xl shadow-shadow-100 dark:shadow-none  dark:!bg-darkMain dark:text-white  max-w-xl p-4 mb-4">
      <div className="mb-4">
        <label className="w-full">Name*</label>
        <input
          type="text"
          value={name}
          onChange={(e) => setName(e.target.value)}
          className={`w-full p-2 border rounded dark:!bg-darkMain `}
        />
        {nameError && name?.length < 1 && (
          <div className="mb-2 rounded-lg bg-red-50 p-2 text-sm text-red-800 dark:bg-gray-800 dark:text-red-500 mt-2 inline-flex">
            {nameError}
          </div>
        )}
      </div>
      <div className="mb-4 ">
        <label className="w-full">Tables*</label>
        <Multiselect
          className="selectBox"
          options={dataFrameNames}
          selectedValues={items}
          onSelect={handleSelect}
          onRemove={handleSelectRemove}
          displayValue="name"
        />
        {dataFramesError && items?.length < 1 && (
          <div className="mb-2 rounded-lg bg-red-50 p-2 text-sm text-red-800 dark:bg-gray-800 dark:text-red-500 mt-2 inline-flex">
            {dataFramesError}
          </div>
        )}
      </div>
      <div className="text-right">
        <button
          className="px-4 py-1 text-md rounded linear bg-[#191919] font-medium text-white transition duration-200 dark:bg-[#191919 dark:text-white dark:hover:bg-[#191919 dark:active:bg-[#191919"
          onClick={handleSubmit}
          disabled={isLoading}
        >
          {isLoading ? <Loader height="h-6" width="w-10" /> : "Save"}
        </button>
      </div>
    </div>
  );
};

export default AddSpaceCard;
