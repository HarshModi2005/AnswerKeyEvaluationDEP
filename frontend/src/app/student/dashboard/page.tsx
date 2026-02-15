"use client"
import { useState } from 'react';
import api from '@/lib/api';
import { Search, CheckCircle, XCircle } from 'lucide-react';

export default function StudentDashboard() {
    const [rollNumber, setRollNumber] = useState('');
    const [results, setResults] = useState<any[]>([]);
    const [searched, setSearched] = useState(false);
    const [loading, setLoading] = useState(false);

    const handleSearch = async () => {
        if (!rollNumber) return;
        setLoading(true);
        try {
            const res = await api.get('/results');
            // Client-side filtering for MVP
            const studentResults = res.data.filter((r: any) =>
                r.student_id && r.student_id.toLowerCase() === rollNumber.toLowerCase()
            );
            setResults(studentResults);
            setSearched(true);
        } catch (error) {
            console.error("Error fetching results:", error);
            alert("Failed to fetch results.");
        }
        setLoading(false);
    };

    return (
        <div className="min-h-screen bg-gray-50 p-8 text-gray-800">
            <div className="max-w-3xl mx-auto">
                <header className="mb-10 text-center">
                    <h1 className="text-3xl font-bold text-gray-900">Student Portal</h1>
                    <p className="text-gray-500">View your assessment results</p>
                </header>

                <div className="bg-white p-8 rounded-2xl shadow-sm mb-8">
                    <label className="block text-sm font-medium text-gray-700 mb-2">Student Roll Number</label>
                    <div className="flex gap-3">
                        <input
                            type="text"
                            placeholder="e.g., 2023CS001"
                            className="flex-1 border border-gray-300 p-3 rounded-xl focus:outline-none focus:ring-2 focus:ring-indigo-500"
                            value={rollNumber}
                            onChange={(e) => setRollNumber(e.target.value)}
                        />
                        <button
                            onClick={handleSearch}
                            className="bg-indigo-600 text-white px-6 py-3 rounded-xl hover:bg-indigo-700 transition flex items-center gap-2 font-medium"
                            disabled={loading}
                        >
                            {loading ? 'Searching...' : <><Search className="w-5 h-5" /> Check Results</>}
                        </button>
                    </div>
                </div>

                {searched && (
                    <div className="space-y-6 animate-in fade-in slide-in-from-bottom-4 duration-500">
                        <h3 className="text-xl font-semibold text-gray-800">Performance History</h3>
                        {results.length === 0 ? (
                            <div className="bg-white p-10 rounded-2xl shadow-sm text-center text-gray-400">
                                No results found for <span className="text-gray-900 font-medium">{rollNumber}</span>.
                            </div>
                        ) : (
                            results.map((res, idx) => (
                                <div key={idx} className="bg-white p-6 rounded-2xl shadow-sm border border-gray-100">
                                    <div className="flex justify-between items-center mb-4 border-b border-gray-100 pb-4">
                                        <div>
                                            <h4 className="text-lg font-bold text-gray-900">Exam: {res.exam_id}</h4>
                                            <p className="text-sm text-gray-500">Submission ID: {res.submission_id.substring(0, 8)}</p>
                                        </div>
                                        <div className="text-right">
                                            <div className="text-3xl font-bold text-indigo-600">{res.score}</div>
                                            <div className="text-xs text-gray-400 uppercase tracking-wide">Total Score</div>
                                        </div>
                                    </div>

                                    <div className="bg-gray-50 p-4 rounded-xl mb-4">
                                        <h5 className="text-sm font-semibold text-gray-700 mb-2">Feedback Summary</h5>
                                        <p className="text-gray-600">{res.feedback}</p>
                                    </div>

                                    {res.details && (() => {
                                        const details = JSON.parse(res.details || '{}');
                                        const answers = details.details || [];
                                        return (
                                            <div className="overflow-x-auto">
                                                <table className="w-full text-sm text-left">
                                                    <thead className="text-xs text-gray-500 uppercase bg-gray-50">
                                                        <tr>
                                                            <th className="px-4 py-2 rounded-l-lg">Q</th>
                                                            <th className="px-4 py-2">Marked</th>
                                                            <th className="px-4 py-2">Correct</th>
                                                            <th className="px-4 py-2 rounded-r-lg">Status</th>
                                                        </tr>
                                                    </thead>
                                                    <tbody>
                                                        {answers.map((ans: any, i: number) => (
                                                            <tr key={i} className="border-b border-gray-50 last:border-0">
                                                                <td className="px-4 py-3 font-medium">{ans.question_number}</td>
                                                                <td className="px-4 py-3">{ans.marked || '-'}</td>
                                                                <td className="px-4 py-3">{ans.correct}</td>
                                                                <td className="px-4 py-3">
                                                                    {ans.is_correct ? (
                                                                        <span className="flex items-center gap-1 text-green-600 font-medium">
                                                                            <CheckCircle className="w-4 h-4" /> Correct
                                                                        </span>
                                                                    ) : (
                                                                        <span className="flex items-center gap-1 text-red-500 font-medium">
                                                                            <XCircle className="w-4 h-4" /> Incorrect
                                                                        </span>
                                                                    )}
                                                                </td>
                                                            </tr>
                                                        ))}
                                                    </tbody>
                                                </table>
                                            </div>
                                        );
                                    })()}
                                </div>
                            ))
                        )}
                    </div>
                )}
            </div>
        </div>
    );
}
