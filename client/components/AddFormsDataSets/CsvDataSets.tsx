import React, { ChangeEvent } from "react";
import { AiOutlineClose } from "react-icons/ai";
import Link from "next/link";
import { FaFileCsv } from "react-icons/fa";
import UploadIcon from "../Icons/UploadIcon";

interface CsvProps {
  handleChange?: (
    event: ChangeEvent<HTMLInputElement | HTMLTextAreaElement>
  ) => void;
  handleOnChange?: (
    event: ChangeEvent<HTMLInputElement | HTMLTextAreaElement>
  ) => void;
  nameError: string | null;
  formData?: {
    name?: string;
    description?: string;
    table?: string;
  };
  descriptionError: string | null;
  csvFileNameSet: string | null;
  setCsvFileNameSet: React.Dispatch<React.SetStateAction<string>>;
  fileError: string;
}
const CsvDataset = ({
  handleChange,
  nameError,
  formData,
  descriptionError,
  handleOnChange,
  csvFileNameSet,
  setCsvFileNameSet,
  fileError,
}: CsvProps) => {
  return (
    <>
      <div className="mt-8">
        <div className="mb-4">
          <label>Name *</label>
          <input
            autoComplete="off"
            onChange={handleChange}
            name="name"
            type="text"
            value={formData?.name}
            className={`w-full mt-1 p-2 border rounded-xl
            ${
              nameError && formData?.name?.length < 1
                ? "border-red-500"
                : "dark:!bg-[#333333] dark:border-none"
            }
            `}
          />
          {nameError && formData?.name?.length < 1 && (
            <div className="mb-2 rounded-lg bg-red-50 p-2 text-sm text-red-800 dark:bg-[#333333] dark:text-red-500 mt-2 inline-flex">
              {nameError}
            </div>
          )}
        </div>
        <div className="mb-4">
          <label>Description</label>
          <textarea
            className={`w-full mt-1 p-2 border rounded-xl
            ${
              descriptionError && formData?.description?.length < 1
                ? "border-red-500"
                : "dark:!bg-[#333333] dark:border-none"
            }
            `}
            onChange={handleChange}
            name="description"
            value={formData?.description}
            placeholder="Describe your table here..."
            rows={4}
          />
        </div>

        <div className="mb-4 relative before:content-[''] before:absolute before:h-[1px] before:bg-[#000] dark:before:bg-white/70 before:w-full before:left-0 before:top-2.5">
          <div className="bg-[white] dark:!bg-darkMain w-max m-auto relative px-4 text-sm text-[#333333] dark:text-white/70">
            Upload your CSV
          </div>
        </div>

        <div className="mb-4">
          <div className="relative max-w-[450px] w-full mx-auto my-2 rounded-xl p-4 py-10 flex flex-col gap-4 items-center justify-center dark:bg-[#333333] border dark:border-none">
            {csvFileNameSet ? (
              <>
                <div className="absolute right-2 top-2">
                  <span
                    className=" rounded   text-sm text-white"
                    style={{ cursor: "pointer" }}
                    onClick={() => {
                      setCsvFileNameSet(null);
                    }}
                  >
                    <AiOutlineClose
                      className="text-[#FF0000] dark:text-white"
                      size="1.5em"
                    />
                  </span>
                </div>
                <FaFileCsv size="3em" />
                <div className="text-sm w-full text-center">
                  {csvFileNameSet}
                </div>
              </>
            ) : (
              <>
                <UploadIcon />
                <input
                  className="absolute h-full w-full z-100 opacity-0"
                  type="file"
                  id="csvFileInput"
                  accept=".csv"
                  onChange={handleOnChange}
                />
                <div className="text-center">
                  <p className="text-xl font-bold">
                    Drag and drop the file here
                  </p>
                  <p>
                    or click{" "}
                    <Link href="#" className="text-orange-400">
                      browse
                    </Link>{" "}
                    to choose a file
                  </p>
                </div>
                {fileError && (
                  <div className="mb-2 rounded-lg bg-red-50 p-2 text-sm text-red-800 dark:bg-gray-800 dark:text-red-500 mt-2 inline-flex">
                    {fileError}
                  </div>
                )}
              </>
            )}
          </div>
        </div>
      </div>
    </>
  );
};

export default CsvDataset;
