import { Loader } from "@/components/loader/Loader";
import React from "react";

const Loading = () => {
  return (
    <div className="flex items-center justify-center w-full h-full mx-auto">
      <Loader />
    </div>
  );
};

export default Loading;
