import { redirect } from "next/navigation";
export default function Home() {
  redirect("/admin/chat");
}
export const dynamic='force-dynamic';

