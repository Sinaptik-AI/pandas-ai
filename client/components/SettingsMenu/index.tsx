import React from "react";
import Image from "next/image";
import Dropdown from "../../components/dropdown";
import { useRouter } from "next/navigation";
import { useQueryClient } from "@tanstack/react-query";
import ToggleDarkModeComponent from "components/ToggleDarkMode";
import Link from "next/link";

const routes = [
  {
    id: 1,
    name: "Settings",
    url: "/settings",
    isAdmin: true,
  },
];

const SettingsMenu = () => {
  const router = useRouter();
  const queryClient = useQueryClient();

  const handleLogOut = () => {
    const mode = localStorage.getItem("mode");
    localStorage.clear();
    localStorage.setItem("mode", mode);
    queryClient.removeQueries();
    router.push("/auth/sign-in");
  };
  return (
    <div className="flex gap-6 items-center px-3">
      <div className="cursor-pointer"></div>
      <Dropdown
        button={
          <Image
            onClick={() => null}
            width="40"
            height="40"
            className="rounded-full cursor-pointer"
            src="https://www.shutterstock.com/image-vector/user-profile-icon-vector-avatar-600nw-2247726673.jpg"
            alt="Gabriele Venturi"
          />
        }
        classNames={"py-2 top-8 -left-[180px] w-max"}
      >
        <div className="flex h-auto w-56 flex-col justify-start rounded-[20px] bg-white bg-cover bg-no-repeat shadow-xl shadow-shadow-500 dark:!bg-darkMain dark:text-white dark:shadow-none">
          <div className="ml-4 mt-3">
            <div className="flex items-center gap-2">
              <p className="text-sm font-bold dark:text-white">
                👋 Welcome back!
              </p>
            </div>
          </div>
          <div className="mt-3 h-px w-full bg-gray-200 dark:bg-white/20 " />

          <div className="p-4 flex flex-col">
            {routes.map((route) => (
              <React.Fragment key={route.id}>
                <Link
                  href={route.url}
                  className="text-sm text-gray-800 dark:text-white hover:dark:text-white cursor-pointer hover:underline mt-1"
                >
                  {route.name}
                </Link>
              </React.Fragment>
            ))}
            <a
              className="mt-2 text-sm font-medium text-red-500 hover:text-red-500 cursor-pointer"
              onClick={handleLogOut}
            >
              Log Out
            </a>
          </div>

          <div className="mt-3 h-px w-full bg-gray-200 dark:bg-white/20 " />

          <div className="flex items-center justify-center py-3">
            <ToggleDarkModeComponent />
          </div>
        </div>
      </Dropdown>
    </div>
  );
};

export default SettingsMenu;
