"use client";
import React, { useEffect, useState } from "react";
import { Switch } from "@/components/ui/switch";
import { Loader } from "@/components/loader/Loader";
import { useGetMe, useUpdateUserRoutes } from "@/hooks/useUsers";
import { toast } from "react-toastify";
import ConfirmationDialog from "@/components/ConfirmationDialog";
import FeatureIcon from "./FeatureIcon";
import AppTooltip from "@/components/AppTooltip";

const GeneralPage = () => {
  const [routes, setRoutes] = useState([]);
  const { data: userResponse, isLoading } = useGetMe();
  const { mutateAsync: updateUserRoutes, isPending } = useUpdateUserRoutes();
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [feature, setFeature] = useState({
    routeName: "",
    featureName: null,
  });

  useEffect(() => {
    if (userResponse) {
      setRoutes(userResponse?.data?.features?.routes || []);
    }
  }, [userResponse]);

  const handleToggle = (routeName, featureName) => {
    let rName: string, fName: string;
    if (!routeName && !featureName) {
      rName = feature.routeName;
      fName = feature.featureName;
    } else {
      rName = routeName;
      fName = featureName;
    }
    const updatedRoutes = routes.map((route) => {
      if (route.name === rName) {
        if (fName) {
          route.features = route.features.map((feature) =>
            feature.name === fName
              ? { ...feature, enabled: !feature.enabled }
              : feature
          );
        } else {
          route.enabled = !route.enabled;
        }
      }
      return route;
    });

    const body = {
      routes: updatedRoutes,
    };
    setRoutes(updatedRoutes);
    updateUserRoutes(body, {
      onSuccess() {
        setIsModalOpen(false);
      },
      onError(error: any) {
        toast.error(
          error?.response?.data?.message
            ? error?.response?.data?.message
            : error.message
        );
      },
    });
  };

  return (
    <>
      <div className="w-full h-full overflow-y-auto custom-scroll mt-5 px-2 md:px-4">
        <h1 className="text-2xl font-bold dark:text-white mb-10">General</h1>
        {isLoading ? (
          <Loader />
        ) : (
          <div className="px-2 md:px-10">
            {routes?.map((route) => (
              <>
                {route?.isEnterprise && (
                  <div className="mt-5" key={route.name}>
                    <AppTooltip text="Disable Logs on/off">
                      <div className="flex gap-5 mb-5">
                        <h2 className="text-xl font-semibold dark:text-white">
                          {route.name}
                        </h2>
                        <FeatureIcon name={route.name} />
                      </div>
                    </AppTooltip>
                    <div className="flex items-center gap-5">
                      <p className="dark:text-white">
                        {route.enabled ? "Disable" : "Enable"}{" "}
                        {route.name.toLowerCase()}
                      </p>
                      <Switch
                        name={route.name}
                        checked={route.enabled}
                        onCheckedChange={() => {
                          if (!route.enabled) {
                            setIsModalOpen(true);
                            setFeature({
                              routeName: route.name,
                              featureName: null,
                            });
                          } else {
                            handleToggle(route.name, null);
                          }
                        }}
                      />
                    </div>
                    {/* Will add features in the future */}
                    {/* {route.features.map((feature) => (
                      <div
                        className="flex items-center gap-5"
                        key={feature.name}
                      >
                        <p className="dark:text-white">
                          Toggle {feature.name.toLowerCase()}
                        </p>
                        <Switch
                          name={`${route.name}-${feature.name}`}
                          checked={feature.enabled}
                          onCheckedChange={() =>
                            handleToggle(route.name, feature.name)
                          }
                        />
                      </div>
                    ))} */}
                  </div>
                )}
              </>
            ))}
          </div>
        )}
      </div>
      {isModalOpen && (
        <ConfirmationDialog
          text={`Are you sure you want to enable enterprise feature?`}
          onCancel={() => {
            setIsModalOpen(false);
          }}
          onSubmit={() => handleToggle(null, null)}
          isLoading={isPending}
        />
      )}
    </>
  );
};

export default GeneralPage;
