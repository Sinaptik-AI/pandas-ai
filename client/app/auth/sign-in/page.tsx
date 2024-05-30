"use client";
import React from "react";

import { Button } from "@/components/ui/button";
import { useRouter } from "next/navigation";

function SignInDefault() {
  const router = useRouter();
  const handleSignIn = async () => {
    localStorage.setItem("is_admin", "true");
    localStorage.setItem("firstName", "arslan");
    localStorage.setItem("lastName", "khan");
    localStorage.setItem(
      "accessToken",
      "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiMzNiMWM5NmQtODQyYi00MTgzLWI5ZWYtODEzZTRkMDEzODZhIiwiZW1haWwiOiJraGFuLmFyc2xhbjM4QGdtYWlsLmNvbSIsIm9yZ2FuaXphdGlvbl9pZCI6ImIyZjg5YTA1LTBjNDEtNGZiZS04MTcxLTY1MmUxMjY4NmRmNiIsImlhdCI6MTcxNjU0NzAwNiwiZXhwIjoxNzE2NjMzNDA2fQ.tjbCINFVGQaP5UAtqGRa2_T69jnkHl1Bjvbnb80k4kM"
    );
    localStorage.setItem(
      "refreshToken",
      "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiMzNiMWM5NmQtODQyYi00MTgzLWI5ZWYtODEzZTRkMDEzODZhIiwiZW1haWwiOiJraGFuLmFyc2xhbjM4QGdtYWlsLmNvbSIsIm9yZ2FuaXphdGlvbl9pZCI6ImIyZjg5YTA1LTBjNDEtNGZiZS04MTcxLTY1MmUxMjY4NmRmNiIsImlhdCI6MTcxNjIyNDE4MCwiZXhwIjoxNzE4ODE2MTgwfQ.fVv27cliWu-mtYIq1jmLKN9Bufd6PLePPoOv219Wl00"
    );
    localStorage.setItem("user_id", "33b1c96d-842b-4183-b9ef-813e4d01386a");
    localStorage.setItem(
      "selectedOrganization",
      `{"id":"b2f89a05-0c41-4fbe-8171-652e12686df6","name":"Sinaptik","url": "www.google.com","is_default": true`
    );
    router.push("/workspace");
  };

  return (
    <div className="flex items-center justify-center mx-auto h-screen dark:bg-black w-full">
      <Button onClick={handleSignIn}>Sign In</Button>
    </div>
  );
}

export default SignInDefault;
