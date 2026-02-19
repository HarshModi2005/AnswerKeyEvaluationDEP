import React, { useState } from 'react';
import { NavLink } from 'react-router-dom';
import Icon from '../AppIcon';

const Sidebar = () => {
    const [collapsed, setCollapsed] = useState(false);

    const navItems = [
        { path: '/dashboard-overview', label: 'Dashboard', icon: 'LayoutDashboard' },
        { path: '/faculty-dashboard', label: 'My Courses', icon: 'BookOpen' }, // New link for Faculty
        { path: '/kanban-board', label: 'Kanban Board', icon: 'Kanban' },
        { path: '/sprint-planning', label: 'Sprint Planning', icon: 'Calendar' },
        { path: '/team-management', label: 'Team', icon: 'Users' },
        { path: '/analytics-dashboard', label: 'Analytics', icon: 'BarChart3' },
    ];

    return (
        <aside className={`fixed top-16 left-0 h-[calc(100vh-4rem)] bg-surface border-r border-border transition-all duration-300 z-50 ${collapsed ? 'w-20' : 'w-64'}`}>
            <div className="flex flex-col h-full py-4">
                {/* Collapse Toggle */}
                <div className="px-4 mb-6 flex justify-end">
                    <button
                        onClick={() => setCollapsed(!collapsed)}
                        className="p-1.5 rounded-md hover:bg-secondary-100 text-secondary-500 transition-colors"
                    >
                        <Icon name={collapsed ? 'ChevronRight' : 'ChevronLeft'} size={16} />
                    </button>
                </div>

                {/* Nav Items */}
                <nav className="flex-1 px-3 space-y-1">
                    {navItems.map((item) => (
                        <NavLink
                            key={item.path}
                            to={item.path}
                            className={({ isActive }) => `
                                flex items-center px-3 py-2.5 rounded-lg transition-colors group
                                ${isActive
                                    ? 'bg-primary-50 text-primary'
                                    : 'text-secondary-600 hover:bg-secondary-50 hover:text-text-primary'
                                }
                            `}
                        >
                            <span className={`${collapsed ? 'mx-auto' : 'mr-3'}`}>
                                <Icon name={item.icon} size={20} />
                            </span>
                            {!collapsed && (
                                <span className="text-sm font-medium truncate">
                                    {item.label}
                                </span>
                            )}

                            {/* Tooltip for collapsed state */}
                            {collapsed && (
                                <div className="absolute left-16 px-2 py-1 bg-secondary-800 text-white text-xs rounded opacity-0 group-hover:opacity-100 pointer-events-none transition-opacity whitespace-nowrap z-50 ml-2">
                                    {item.label}
                                </div>
                            )}
                        </NavLink>
                    ))}
                </nav>

                {/* Bottom Section */}
                <div className="mt-auto px-3 pt-4 border-t border-border">
                    <NavLink
                        to="/settings"
                        className="flex items-center px-3 py-2.5 rounded-lg text-secondary-600 hover:bg-secondary-50 hover:text-text-primary transition-colors"
                    >
                        <span className={`${collapsed ? 'mx-auto' : 'mr-3'}`}>
                            <Icon name="Settings" size={20} />
                        </span>
                        {!collapsed && (
                            <span className="text-sm font-medium">Settings</span>
                        )}
                    </NavLink>
                </div>
            </div>
        </aside>
    );
};

export default Sidebar;
