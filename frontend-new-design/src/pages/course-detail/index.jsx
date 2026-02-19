import React, { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import Header from '../../components/ui/Header';
import Sidebar from '../../components/ui/Sidebar';
import PageHeader from '../../components/ui/PageHeader';
import Icon from '../../components/AppIcon';
import MetricsCard from '../dashboard-overview/components/MetricsCard';

const CourseDetail = () => {
    const { courseId } = useParams();
    const navigate = useNavigate();
    const [activeTab, setActiveTab] = useState('overview');

    // Mock specific course data (ideally fetched based on courseId)
    const courseData = {
        id: courseId,
        title: 'Data Structures & Algorithms',
        code: 'CS 101',
        description: 'Advanced algorithms and data structures.',
        semester: 'Spring 2024',
        instructor: 'Dr. Jane Smith',
        totalStudents: 89,
        assignments: 5,
        averageGrade: '84%'
    };

    const tabs = [
        { id: 'overview', label: 'Overview', icon: 'LayoutDashboard' },
        { id: 'assignments', label: 'Assignments', icon: 'FileText' },
        { id: 'students', label: 'Students', icon: 'Users' },
        { id: 'settings', label: 'Settings', icon: 'Settings' },
    ];

    return (
        <div className="min-h-screen bg-background">
            <Header />
            <Sidebar />

            <main className="lg:ml-64 pt-16 transition-all duration-300">
                <div className="p-6 max-w-7xl mx-auto space-y-6">
                    {/* Breadcrumb / Back Navigation */}
                    <div className="flex items-center text-sm text-text-secondary mb-4">
                        <button onClick={() => navigate('/faculty-dashboard')} className="hover:text-primary transition-colors flex items-center">
                            <Icon name="ArrowLeft" size={14} className="mr-1" />
                            Back to Courses
                        </button>
                        <span className="mx-2">/</span>
                        <span className="font-medium text-text-primary">{courseData.code}</span>
                    </div>

                    <PageHeader
                        title={courseData.title}
                        description={`${courseData.code} • ${courseData.semester}`}
                        actions={
                            <div className="flex space-x-3">
                                <button className="px-4 py-2 border border-border bg-surface text-text-secondary rounded-lg hover:bg-secondary-50 transition-colors">
                                    Edit Course
                                </button>
                                <button className="px-4 py-2 bg-primary text-white rounded-lg hover:bg-primary-700 transition-colors shadow-sm flex items-center">
                                    <Icon name="Plus" size={16} className="mr-2" />
                                    <span>New Assignment</span>
                                </button>
                            </div>
                        }
                    />

                    {/* Stats Row */}
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                        <MetricsCard
                            title="Total Students"
                            value={courseData.totalStudents}
                            icon="Users"
                            color="primary"
                            trend="+2 this week"
                        />
                        <MetricsCard
                            title="Assignments"
                            value={courseData.assignments}
                            icon="FileText"
                            color="secondary"
                            trend="2 active"
                        />
                        <MetricsCard
                            title="Average Grade"
                            value={courseData.averageGrade}
                            icon="Award"
                            color="success"
                            trend="+5% vs last sem"
                        />
                    </div>

                    {/* Tabs Navigation */}
                    <div className="border-b border-border mb-6">
                        <nav className="-mb-px flex space-x-8" aria-label="Tabs">
                            {tabs.map((tab) => (
                                <button
                                    key={tab.id}
                                    onClick={() => setActiveTab(tab.id)}
                                    className={`
                                        group inline-flex items-center py-4 px-1 border-b-2 font-medium text-sm transition-colors
                                        ${activeTab === tab.id
                                            ? 'border-primary text-primary'
                                            : 'border-transparent text-text-secondary hover:text-text-primary hover:border-secondary-300'
                                        }
                                    `}
                                >
                                    <Icon
                                        name={tab.icon}
                                        size={18}
                                        className={`mr-2 ${activeTab === tab.id ? 'text-primary' : 'text-secondary-400 group-hover:text-secondary-500'}`}
                                    />
                                    {tab.label}
                                </button>
                            ))}
                        </nav>
                    </div>

                    {/* Tab Content */}
                    <div className="bg-surface border border-border rounded-xl p-6 min-h-[400px]">
                        {activeTab === 'overview' && (
                            <div className="space-y-6">
                                <h3 className="text-lg font-medium text-text-primary">Recent Activity</h3>
                                <p className="text-text-secondary">No recent activity to show.</p>
                            </div>
                        )}
                        {activeTab === 'assignments' && (
                            <div className="space-y-6">
                                <h3 className="text-lg font-medium text-text-primary">Assignments</h3>
                                <div className="border rounded-lg p-4 flex justify-between items-center hover:bg-secondary-50 transition-colors cursor-pointer">
                                    <div>
                                        <h4 className="font-medium text-text-primary">Assignment 1: Linked Lists</h4>
                                        <p className="text-sm text-text-secondary">Due: Oct 15, 2024</p>
                                    </div>
                                    <div className="flex items-center space-x-4">
                                        <span className="px-2 py-1 bg-success-50 text-success-700 text-xs rounded-full font-medium">Published</span>
                                        <Icon name="ChevronRight" size={20} className="text-secondary-400" />
                                    </div>
                                </div>
                            </div>
                        )}
                        {activeTab === 'students' && (
                            <div className="space-y-6">
                                <h3 className="text-lg font-medium text-text-primary">Students List</h3>
                                <div className="overflow-x-auto">
                                    <table className="min-w-full divide-y divide-border">
                                        <thead className="bg-secondary-50">
                                            <tr>
                                                <th className="px-6 py-3 text-left text-xs font-medium text-text-secondary uppercase tracking-wider">Name</th>
                                                <th className="px-6 py-3 text-left text-xs font-medium text-text-secondary uppercase tracking-wider">Roll No</th>
                                                <th className="px-6 py-3 text-left text-xs font-medium text-text-secondary uppercase tracking-wider">Status</th>
                                            </tr>
                                        </thead>
                                        <tbody className="bg-surface divide-y divide-border">
                                            {[1, 2, 3].map((i) => (
                                                <tr key={i}>
                                                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-text-primary">Student {i}</td>
                                                    <td className="px-6 py-4 whitespace-nowrap text-sm text-text-secondary">2023CS{100 + i}</td>
                                                    <td className="px-6 py-4 whitespace-nowrap">
                                                        <span className="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-success-100 text-success-800">
                                                            Active
                                                        </span>
                                                    </td>
                                                </tr>
                                            ))}
                                        </tbody>
                                    </table>
                                </div>
                            </div>
                        )}
                        {activeTab === 'settings' && (
                            <div className="space-y-6">
                                <h3 className="text-lg font-medium text-text-primary">Course Settings</h3>
                                <p className="text-text-secondary">Archive course, manage permissions, etc.</p>
                            </div>
                        )}
                    </div>
                </div>
            </main>
        </div>
    );
};

export default CourseDetail;
