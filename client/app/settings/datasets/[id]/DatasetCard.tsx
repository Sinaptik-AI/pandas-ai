import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import ConfirmationDialog from "components/ConfirmationDialog";
import Card from "components/card";
import { useRouter } from "next/navigation";
import React, { useState } from "react";
import { toast } from "react-toastify";
import { IDatasetDetails } from "../datasets-interface";
import { convertToCSV } from "@/utils/convertToCSV";
import { useDeleteDataset, useUpdateDatasetCard } from "@/hooks/useDatasets";
import { Loader } from "@/components/loader/Loader";
import { DeleteDataset } from "@/services/datasets";
import { axiosInstance } from "@/utils/apiUtils";

interface IProps {
  dataframe: IDatasetDetails;
}

const DatasetCard = ({ dataframe }: IProps) => {
  const [isEditFormOpen, setIsEditFormOpen] = useState(false);
  const [isDeleteLoading, setIsDeleteLoading] = useState(false);
  const [isDeleteModalOpen, setIsDeleteModalOpen] = useState(false);
  const [isDownloadLoading, setIsDownloadLoading] = useState(false);

  const { mutateAsync: editDatasetCard, isPending: isEditDatasetLoading } =
    useUpdateDatasetCard();
  const { mutateAsync: deleteDatasetCard, isPending: isDeleteDatasetLoading } =
    useDeleteDataset();

  const [datasetForm, setDatasetForm] = useState({
    name: dataframe?.name,
    description: dataframe?.description,
  });

  const router = useRouter();

  const handleChange = (e) => {
    const { name, value } = e.target;
    setDatasetForm({
      ...datasetForm,
      [name]: value,
    });
  };

  const onSuccess = (response: any) => {
    toast.success(response?.data?.message);
    setIsEditFormOpen(false);
    setIsDeleteModalOpen(false);
  };

  const onError = (error: any) => {
    toast.error(
      error?.response?.data?.message
        ? error?.response?.data?.message
        : error.message
    );
  };

  const handleSubmit = async () => {
    const dataSet = {
      name: datasetForm.name,
      description: datasetForm.description,
    };
    editDatasetCard(
      {
        id: dataframe.id,
        body: dataSet,
      },
      { onSuccess, onError }
    );
  };

  const handleDownload = async () => {
    setIsDownloadLoading(true);
    await axiosInstance
      .get(`/v1/datasets/download/${dataframe.id}`, {
        responseType: "blob",
      })
      .then((response) => {
        const url = window.URL.createObjectURL(new Blob([response.data]));
        const link = document.createElement("a");
        link.href = url;
        link.setAttribute("download", `${dataframe.id}.csv`);
        document.body.appendChild(link);
        link.click();
        // Cleanup
        link.parentNode.removeChild(link);
        window.URL.revokeObjectURL(url);
      })
      .catch((error) => {
        toast.error(
          error?.response?.data?.message
            ? error?.response?.data?.message
            : error?.message
        );
      });
  };

  const handleDelete = async () => {
    deleteDatasetCard(
      {
        id: dataframe.id,
      },
      {
        onSuccess(response) {
          toast.success(response?.data?.message);
          setIsDeleteModalOpen(false);
          router.push("/settings/datasets");
        },
        onError(error: any) {
          toast.error(
            error?.response?.data?.message
              ? error?.response?.data?.message
              : error?.message
          );
        },
      }
    );
  };

  return (
    <>
      {!isEditFormOpen ? (
        <Card extra={"w-full py-4 px-6 h-full mb-4"}>
          <div className="flex flex-col justify-between min-h-[170px]">
            <div>
              <h3 className="font-bold text-[20px] mb-1">
                {datasetForm?.name}
              </h3>
              <h3 className="font-bold text-sm mb-1">
                <span className="font-normal">{datasetForm?.description}</span>
              </h3>
            </div>
            <div className="flex justify-start gap-4 items-center">
              <Button
                type="button"
                onClick={() => {
                  setIsEditFormOpen(true);
                }}
                disabled={isEditDatasetLoading || isDeleteDatasetLoading}
              >
                Edit
              </Button>
              <Button
                type="button"
                onClick={() => {
                  handleDownload();
                }}
                disabled={isEditDatasetLoading || isDeleteDatasetLoading}
              >
                Download
              </Button>
              <Button
                type="button"
                variant="destructive"
                disabled={isEditDatasetLoading || isDeleteDatasetLoading}
                onClick={() => setIsDeleteModalOpen(true)}
              >
                Delete
              </Button>
            </div>
          </div>
        </Card>
      ) : (
        <Card extra={"w-full py-4 px-6 h-full mb-4"}>
          <div className="flex flex-col justify-between min-h-[170px]">
            <div className="mt-2">
              <Input
                name="name"
                type="text"
                placeholder="Add Dataset name"
                autoComplete="off"
                value={datasetForm.name}
                onChange={handleChange}
              />
            </div>
            <div className="mt-1">
              <Textarea
                name="description"
                placeholder="Add Dataset name"
                autoComplete="off"
                value={datasetForm.description}
                onChange={handleChange}
              />
            </div>

            <div className="flex justify-start gap-4 items-center flex-wrap">
              <Button
                type="button"
                onClick={() => {
                  handleSubmit();
                }}
                disabled={isEditDatasetLoading || isDeleteDatasetLoading}
              >
                {isEditDatasetLoading ? (
                  <Loader height="h-6" width="w-10" />
                ) : (
                  "Save"
                )}
              </Button>
              <Button
                type="button"
                variant="destructive"
                disabled={isEditDatasetLoading || isDeleteDatasetLoading}
                onClick={() => setIsEditFormOpen(false)}
              >
                Cancel
              </Button>
            </div>
          </div>
        </Card>
      )}

      {isDeleteModalOpen && (
        <ConfirmationDialog
          text={`Are you sure you want to delete this Datasets?`}
          onCancel={() => {
            setIsDeleteModalOpen(false);
          }}
          isLoading={isDeleteLoading}
          onSubmit={handleDelete}
        />
      )}
    </>
  );
};

export default DatasetCard;
