import Link from "next/link";
import { ArrowRight } from "lucide-react";

export default function Home() {
  return (
    <div className="min-h-screen flex flex-col items-center justify-center bg-gradient-to-br from-indigo-50 to-blue-100 p-4">
      <div className="bg-white p-10 rounded-2xl shadow-xl max-w-lg w-full text-center">
        <h1 className="text-4xl font-extrabold text-transparent bg-clip-text bg-gradient-to-r from-blue-600 to-indigo-600 mb-4">
          AutoEval
        </h1>
        <p className="text-gray-600 mb-8 text-lg">
          Automated Answer Sheet Evaluation System driven by AI.
        </p>

        <div className="space-y-4">
          <Link
            href="/admin/dashboard"
            className="flex items-center justify-center gap-2 w-full bg-blue-600 hover:bg-blue-700 text-white font-semibold py-3 px-6 rounded-lg transition-all shadow-md hover:shadow-lg"
          >
            Go to Instructor Dashboard <ArrowRight className="w-5 h-5" />
          </Link>

          <Link
            href="/student/dashboard"
            className="flex items-center justify-center gap-2 w-full bg-indigo-600 hover:bg-indigo-700 text-white font-semibold py-3 px-6 rounded-lg transition-all shadow-md hover:shadow-lg"
          >
            Student Portal
          </Link>
        </div>
      </div>
    </div>
  );
}
