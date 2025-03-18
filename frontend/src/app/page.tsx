import Link from "next/link";

export default function Home() {
  return (
    <div className="flex flex-col space-y-4 items-center justify-center h-screen">
      <input className="border-2 border-gray-300 p-2" type="text" placeholder="Enter your GitHub url" />
      <Link href="/graphrender">
        <button className="bg-white text-black p-2 ">Submit</button>
      </Link>
    </div>
  );
}
