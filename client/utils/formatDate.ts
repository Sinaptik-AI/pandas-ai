import { formatDistanceToNow } from "date-fns";

export const FormatDate = (timestamp: string) => {
  const currentDate = new Date(timestamp);
  const timeAgo = formatDistanceToNow(currentDate, { addSuffix: true });
  return timeAgo;
};
