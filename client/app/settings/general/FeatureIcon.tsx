"use client";
import React from "react";
import { TbLogs } from "react-icons/tb";

const LogoMap = {
  Logs: <TbLogs />,
  default: <TbLogs />,
};

interface IProps {
  name: string;
}
const FeatureIcon = ({ name }: IProps) => {
  const logo = LogoMap[name] || LogoMap.default;

  return <div className="flex items-center justify-center">{logo}</div>;
};

export default FeatureIcon;
