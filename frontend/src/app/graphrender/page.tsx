import Link from "next/link";

export default function GraphRender() {
    return (
        <div className="flex flex-col space-y-4 items-center justify-center h-screen">
            <div className="w-full max-w-[80vh] h-[80vh] border-2 border-gray-300 flex items-center justify-center">
                <p className="text-gray-400">Diagram will appear here</p>
            </div>
            <input className="w-full max-w-[80vh] border-2 border-gray-300 p-2" type="text" placeholder="Enter your question" />

            <Link href="/graphrender" className="w-full max-w-[80vh]">
                <button className="bg-white text-black p-2 w-full hover:cursor-pointer">Ask</button>
            </Link>
        </div>
    );
}
