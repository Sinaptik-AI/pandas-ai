"use client";
import { useState, useEffect } from "react";
import { usePathname, useRouter } from "next/navigation";
import { useGetMe } from "./useUsers";

const usePermissionCheck = () => {
  const [hasPermission, setHasPermission] = useState(false);
  const path = usePathname();
  const router = useRouter();
  const { data: userResponse } = useGetMe();

  useEffect(() => {
    if (userResponse) {
      const route = userResponse?.data?.features?.routes?.find(
        (route) => route.path === path.toString()
      );

      if (route && route.enabled) {
        setHasPermission(true);
      } else {
        setHasPermission(false);
        router.push("/settings");
      }
    }
  }, [userResponse]);

  return hasPermission;
};

export default usePermissionCheck;
