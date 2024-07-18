"use client";
import Card from "@/components/card";
import ConfirmationDialog from "@/components/ConfirmationDialog";
import { Button } from "@/components/ui/button";
import { useDeleteWorkspace } from "@/hooks/useSpaces";
import { revalidateWorkspaces } from "@/lib/actions";
import Link from "next/link";
import { useRouter } from "next/navigation";
import React, { useState } from "react";
import { toast } from "react-toastify";

interface IProps {
  data: any;
}

const WorkspaceCard = ({ data }: IProps) => {
  const [isDeleteModalOpen, setIsDeleteModalOpen] = useState(false);
  const { isPending, mutateAsync: deleteSpace } = useDeleteWorkspace();
  const router = useRouter();

  const handleDeleteSpace = () => {
    deleteSpace(
      { id: data.id },
      {
        onSuccess(response) {
          toast.success(response?.data?.message);
          setIsDeleteModalOpen(false);
          revalidateWorkspaces();
          router.push("/settings/workspaces");
        },
        onError(error) {
          toast.error(error?.message);
        },
      }
    );
  };
  return (
    <>
      <Card extra={"w-full py-4 px-6 h-full mb-4"}>
        <div className="flex flex-col justify-between min-h-[300px]">
          <div>
            <h3 className="font-bold text-[20px] mb-1">{data?.name}</h3>
            <h3 className="font-bold text-sm mb-1">
              <span className="font-normal">
                {`This is the workspace dedicated to the ${data?.name} team.`}
              </span>
            </h3>
          </div>
          <div className="flex justify-start gap-4 items-center flex-wrap">
            <Link href={`/settings/workspaces/editspaces?id=${data?.id}`}>
              <Button>Edit</Button>
            </Link>

            <div
              onClick={() => {
                setIsDeleteModalOpen(true);
              }}
              className={`px-8 py-1 rounded-[10px] flex flex-wrap items-center justify-center cursor-pointer dark:bg-[#D30000] neon-on-hovers`}
            >
              <span className="font-bold text-white">Delete</span>
            </div>
          </div>
        </div>
      </Card>
      {isDeleteModalOpen && (
        <ConfirmationDialog
          text={`Are you sure you want to delete this Workspace?`}
          onCancel={() => {
            setIsDeleteModalOpen(false);
          }}
          onSubmit={handleDeleteSpace}
          isLoading={isPending}
        />
      )}
    </>
  );
};

export default WorkspaceCard;
