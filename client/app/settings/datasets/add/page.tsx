"use client";
import React, { useState } from "react";
import { Loader } from "components/loader/Loader";
import { FaFileCsv } from "react-icons/fa";
import Link from "next/link";
import CsvDataset from "@/components/AddFormsDataSets/CsvDataSets";
import { ValidationErrorsAddForm } from "../datasets-interface";
import { Button } from "@/components/ui/button";
import { useCreateDataset } from "@/hooks/useDatasets";
import { toast } from "react-toastify";
import { useRouter } from "next/navigation";

const AddDataSet = () => {
  const [inputFile, setInputFile] = useState(null);
  const [validationErrors, setValidationErrors] =
    useState<ValidationErrorsAddForm>({});
  const [fileError, setFileError] = useState("");

  const { mutateAsync: createDataset, isPending } = useCreateDataset();
  const router = useRouter();

  const handleFormOnChange = (e) => {
    const file = e.target.files[0];
    const fileType = file?.name?.split(".").pop().toLowerCase();
    if (fileType !== "csv") {
      setFileError("Please upload a CSV file.");
      return;
    }

    setInputFile(e.target.files[0]);
  };

  const [formData, setFormData] = useState({
    name: "",
    description: "",
  });

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData({
      ...formData,
      [name]: value,
    });
  };

  const dataSetsRequiredFields = {
    CSV: ["name"],
  };

  const validateForm = () => {
    const errors = {};
    const requiredFields = dataSetsRequiredFields["CSV"] || [];

    for (const field of requiredFields) {
      if (formData[field]?.trim() === "") {
        errors[field] = `${
          field.charAt(0).toUpperCase() + field.slice(1)
        } field is required`;
      }
    }

    setValidationErrors(errors);
    return Object.keys(errors)?.length === 0;
  };

  const resetForm = () => {
    setFormData({
      name: "",
      description: "",
    });
  };
  const handleAdd = async () => {
    if (!validateForm()) {
      return;
    }
    if (!inputFile) {
      setFileError("No file selected. Please select a file.");
      return;
    }

    const formBody = new FormData();
    formBody.append("name", formData.name);
    formBody.append("description", formData.description);
    formBody.append("file", inputFile);

    createDataset({ formBody }, { onSuccess, onError });
  };
  const onSuccess = (response: any) => {
    toast.success(response?.data?.message);
    router.push("/settings/datasets");
  };

  const onError = (error: any) => {
    toast.error(
      error?.response?.data?.message
        ? error?.response?.data?.message
        : error.message
    );
  };

  return (
    <div className="w-full h-full overflow-y-auto custom-scroll mt-5 px-2 md:px-4">
      <h1 className="text-2xl font-bold dark:text-white mb-10">
        <Link href="/settings/datasets">Datasets</Link>
        <small> › New</small>
      </h1>
      {isPending ? (
        <Loader />
      ) : (
        <div className="!z-5 relative rounded-[20px] bg-white bg-clip-border shadow-3xl shadow-shadow-100 dark:shadow-none dark:bg-darkMain dark:text-white max-w-3xl p-4 mb-4 m-5 mt-10">
          <div className="flex w-full items-center gap-2 flex-wrap md:flex-nowrap">
            <div className="border flex items-center justify-center md:h-20 md:w-24 md:p-2 py-2 px-4 rounded cursor-pointer bg-black text-white">
              <div className="flex gap-1 justify-center flex-col">
                <span className="m-auto">
                  <FaFileCsv size="2em" />
                </span>
                CSV
              </div>
            </div>
          </div>

          <CsvDataset
            handleChange={handleChange}
            handleOnChange={handleFormOnChange}
            nameError={validationErrors.name}
            formData={formData}
            descriptionError={validationErrors.description}
            csvFileNameSet={inputFile?.name}
            setCsvFileNameSet={setInputFile}
            fileError={fileError}
          />

          <div className="text-center">
            <Button onClick={handleAdd}>Add dataset</Button>
          </div>
        </div>
      )}
    </div>
  );
};
export default AddDataSet;
