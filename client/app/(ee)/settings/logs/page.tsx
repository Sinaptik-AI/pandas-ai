import React from "react";
import { GetLogs } from "@/services/logs";
import LogsCard from "./logs-card";

export const dynamic = "force-dynamic";

export default async function Logs() {
	const data = await GetLogs();

	return (
		<div className="w-full h-full overflow-y-auto custom-scroll mt-5 px-2 md:px-4">
			<h1 className="text-2xl font-bold dark:text-white mb-10">Logs</h1>
			<LogsCard logs={data?.logs || []} logs_count={data?.logs_count} />
		</div>
	);
}
