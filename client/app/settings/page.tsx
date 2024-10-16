import { redirect } from "next/navigation";
export default function Home() {
  redirect("/settings/datasets");
}
export const dynamic='force-dynamic';

