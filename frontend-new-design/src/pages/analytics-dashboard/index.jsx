import React, { useState } from 'react';
import Header from '../../components/ui/Header';
import Sidebar from '../../components/ui/Sidebar';
import PageHeader from '../../components/ui/PageHeader';
import Icon from '../../components/AppIcon';
import MetricsCard from '../dashboard-overview/components/MetricsCard';

// Mock specific exam analytics data
const examAnalytics = {
    'CS306 Quiz 1': {
        averageScore: '78%',
        medianScore: '82%',
        highestScore: '98%',
        lowestScore: '45%',
        totalStudents: 120,
        gradedCount: 115,
        difficulty: 'Medium',
        distribution: [
            { range: '0-40', count: 5 },
            { range: '41-60', count: 12 },
            { range: '61-80', count: 45 },
            { range: '81-100', count: 53 },
        ],
        hardestQuestion: { id: 'Q4', topic: 'Dynamic Programming', correctRate: '35%' },
        easiestQuestion: { id: 'Q1', topic: 'Basic Arrays', correctRate: '92%' }
    },
    'CS306 Midsem': {
        averageScore: '65%',
        medianScore: '68%',
        highestScore: '95%',
        lowestScore: '30%',
        totalStudents: 118,
        gradedCount: 45,
        difficulty: 'Hard',
        distribution: [
            { range: '0-40', count: 15 },
            { range: '41-60', count: 35 },
            { range: '61-80', count: 40 },
            { range: '81-100', count: 28 },
        ],
        hardestQuestion: { id: 'Q3', topic: 'Graph Theory', correctRate: '25%' },
        easiestQuestion: { id: 'Q8', topic: 'Sorting', correctRate: '88%' }
    }
};

const AnalyticsDashboard = () => {
    const [selectedExam, setSelectedExam] = useState(null);

    const exams = [
        { id: 'CS306 Quiz 1', name: 'CS306 Quiz 1', date: 'Feb 10, 2024', status: 'Graded' },
        { id: 'CS306 Midsem', name: 'CS306 Midsem', date: 'Mar 15, 2024', status: 'In Progress' },
    ];

    const handleExamClick = (examId) => {
        setSelectedExam(examId);
    };

    const handleBack = () => {
        setSelectedExam(null);
    };

    const currentAnalytics = selectedExam ? examAnalytics[selectedExam] : null;

    return (
        <div className="min-h-screen bg-background">
            <Header />
            <Sidebar />

            <main className="lg:ml-60 pt-16">
                <div className="p-6 max-w-7xl mx-auto space-y-6">
                    {/* Index View: List of Exams */}
                    {!selectedExam && (
                        <>
                            <PageHeader
                                title="Exam Analytics"
                                description="Select an exam to view detailed performance metrics."
                            />
                            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                                {exams.map((exam) => (
                                    <div
                                        key={exam.id}
                                        onClick={() => handleExamClick(exam.id)}
                                        className="bg-surface border border-border rounded-xl p-6 hover:shadow-md transition-shadow cursor-pointer group"
                                    >
                                        <div className="flex items-center justify-between mb-4">
                                            <div className="w-10 h-10 bg-primary-100 rounded-lg flex items-center justify-center text-primary-700 group-hover:bg-primary group-hover:text-white transition-colors">
                                                <Icon name="FileText" size={20} />
                                            </div>
                                            <span className={`px-2 py-1 rounded text-xs font-medium ${exam.status === 'Graded' ? 'bg-success-100 text-success-700' : 'bg-warning-100 text-warning-700'}`}>
                                                {exam.status}
                                            </span>
                                        </div>
                                        <h3 className="text-lg font-semibold text-text-primary mb-1">{exam.name}</h3>
                                        <p className="text-sm text-text-secondary mb-4">Conducted on {exam.date}</p>
                                        <div className="flex items-center text-sm text-primary group-hover:underline">
                                            View Analytics <Icon name="ArrowRight" size={14} className="ml-1" />
                                        </div>
                                    </div>
                                ))}
                            </div>
                        </>
                    )}

                    {/* Detail View: Exam Specific Analytics */}
                    {selectedExam && currentAnalytics && (
                        <div className="space-y-6">
                            <div className="flex items-center text-sm text-text-secondary mb-4">
                                <button onClick={handleBack} className="hover:text-primary transition-colors flex items-center">
                                    <Icon name="ArrowLeft" size={14} className="mr-1" />
                                    Back to Exams
                                </button>
                                <span className="mx-2">/</span>
                                <span className="font-medium text-text-primary">{selectedExam}</span>
                            </div>

                            <PageHeader
                                title={`${selectedExam} Analytics`}
                                description={`Performance overview and statistics.`}
                                actions={
                                    <button className="px-4 py-2 border border-border bg-surface text-text-secondary rounded-lg hover:bg-secondary-50 transition-colors flex items-center">
                                        <Icon name="Download" size={16} className="mr-2" />
                                        Export Report
                                    </button>
                                }
                            />

                            {/* Key Metrics Row */}
                            <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
                                <MetricsCard title="Average Score" value={currentAnalytics.averageScore} icon="BarChart2" color="primary" />
                                <MetricsCard title="Median Score" value={currentAnalytics.medianScore} icon="Activity" color="secondary" />
                                <MetricsCard title="Highest Score" value={currentAnalytics.highestScore} icon="TrendingUp" color="success" />
                                <MetricsCard title="Graded Papers" value={`${currentAnalytics.gradedCount}/${currentAnalytics.totalStudents}`} icon="CheckCircle" color="warning" />
                            </div>

                            {/* Detailed Analysis Section */}
                            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                                {/* Score Distribution (Mock Histogram) */}
                                <div className="bg-surface border border-border rounded-xl p-6">
                                    <h3 className="text-lg font-medium text-text-primary mb-4">Score Distribution</h3>
                                    <div className="space-y-4">
                                        {currentAnalytics.distribution.map((item, index) => (
                                            <div key={index} className="flex items-center">
                                                <span className="w-16 text-sm text-text-secondary">{item.range}</span>
                                                <div className="flex-1 h-4 bg-secondary-100 rounded-full mx-3 overflow-hidden">
                                                    <div
                                                        className="h-full bg-primary rounded-full"
                                                        style={{ width: `${(item.count / currentAnalytics.totalStudents) * 100}%` }}
                                                    ></div>
                                                </div>
                                                <span className="w-8 text-sm text-text-primary text-right">{item.count}</span>
                                            </div>
                                        ))}
                                    </div>
                                </div>

                                {/* Question Analysis */}
                                <div className="bg-surface border border-border rounded-xl p-6">
                                    <h3 className="text-lg font-medium text-text-primary mb-4">Question Analysis</h3>
                                    <div className="space-y-4">
                                        <div className="p-4 bg-error-50 border border-error-100 rounded-lg">
                                            <div className="flex items-center text-error-700 mb-2">
                                                <Icon name="AlertTriangle" size={18} className="mr-2" />
                                                <span className="font-semibold">Hardest Question</span>
                                            </div>
                                            <p className="text-text-primary font-medium">{currentAnalytics.hardestQuestion.id}: {currentAnalytics.hardestQuestion.topic}</p>
                                            <p className="text-sm text-text-secondary">Only {currentAnalytics.hardestQuestion.correctRate} correct answers</p>
                                        </div>
                                        <div className="p-4 bg-success-50 border border-success-100 rounded-lg">
                                            <div className="flex items-center text-success-700 mb-2">
                                                <Icon name="Check" size={18} className="mr-2" />
                                                <span className="font-semibold">Easiest Question</span>
                                            </div>
                                            <p className="text-text-primary font-medium">{currentAnalytics.easiestQuestion.id}: {currentAnalytics.easiestQuestion.topic}</p>
                                            <p className="text-sm text-text-secondary">{currentAnalytics.easiestQuestion.correctRate} correct answers</p>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    )}
                </div>
            </main>
        </div>
    );
};

export default AnalyticsDashboard;