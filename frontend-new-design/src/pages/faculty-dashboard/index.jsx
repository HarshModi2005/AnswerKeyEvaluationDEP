import React from 'react';
import { useNavigate } from 'react-router-dom';
import Header from '../../components/ui/Header';
import Sidebar from '../../components/ui/Sidebar';
import PageHeader from '../../components/ui/PageHeader';
import CourseCard from './components/CourseCard';
import Icon from '../../components/AppIcon';

const FacultyDashboard = () => {
    const navigate = useNavigate();

    // Mock Faculty Data
    const mockCourses = [
        {
            id: 'CS101',
            title: 'Introduction to Computer Science',
            code: 'CS 101',
            description: 'Fundamentals of programming and computer systems.',
            studentCount: 124,
            pendingTasks: 3,
            color: 'from-blue-500 to-blue-600 bg-gradient-to-r'
        },
        {
            id: 'CS202',
            title: 'Data Structures & Algorithms',
            code: 'CS 202',
            description: 'Advanced algorithms and data structures.',
            studentCount: 89,
            pendingTasks: 1,
            color: 'from-emerald-500 to-emerald-600 bg-gradient-to-r'
        },
        {
            id: 'CS305',
            title: 'Software Engineering Principles',
            code: 'CS 305',
            description: 'Methodologies for building large-scale software systems.',
            studentCount: 56,
            pendingTasks: 5,
            color: 'from-purple-500 to-purple-600 bg-gradient-to-r'
        },
        {
            id: 'CS450',
            title: 'Artificial Intelligence',
            code: 'CS 450',
            description: 'Introduction to AI and machine learning concepts.',
            studentCount: 42,
            pendingTasks: 0,
            color: 'from-orange-500 to-orange-600 bg-gradient-to-r'
        },
    ];

    return (
        <div className="min-h-screen bg-background">
            <Header />
            <Sidebar />

            <main className="lg:ml-64 pt-16 transition-all duration-300">
                <div className="p-6 max-w-7xl mx-auto space-y-6">
                    <PageHeader
                        title="My Courses"
                        description="Manage your active courses and assessments."
                        actions={
                            <button className="flex items-center px-4 py-2 bg-primary text-white rounded-lg hover:bg-primary-700 transition-colors shadow-sm">
                                <Icon name="Plus" size={16} className="mr-2" />
                                <span>Create New Course</span>
                            </button>
                        }
                    />

                    {/* Course Filter / Search Bar (Optional) */}
                    <div className="flex items-center space-x-4 mb-6">
                        <div className="relative flex-1 max-w-md">
                            <Icon name="Search" className="absolute left-3 top-1/2 -translate-y-1/2 text-secondary-400" size={18} />
                            <input
                                type="text"
                                placeholder="Search by course name or code..."
                                className="w-full pl-10 pr-4 py-2 border border-border rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent outline-none transition-all"
                            />
                        </div>
                        <select className="px-4 py-2 border border-border rounded-lg bg-surface text-text-secondary focus:ring-2 focus:ring-primary-500 outline-none">
                            <option>All Semesters</option>
                            <option>Fall 2023</option>
                            <option>Spring 2024</option>
                        </select>
                    </div>

                    {/* Course Grid */}
                    {mockCourses.length > 0 ? (
                        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
                            {mockCourses.map(course => (
                                <CourseCard key={course.id} course={course} />
                            ))}
                        </div>
                    ) : (
                        <div className="text-center py-20 bg-surface rounded-xl border border-dashed border-border">
                            <div className="bg-secondary-50 w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4">
                                <Icon name="BookOpen" size={32} className="text-secondary-400" />
                            </div>
                            <h3 className="text-lg font-medium text-text-primary">No courses found</h3>
                            <p className="text-secondary-500 mt-1">Get started by creating your first course.</p>
                        </div>
                    )}
                </div>
            </main>
        </div>
    );
};

export default FacultyDashboard;
