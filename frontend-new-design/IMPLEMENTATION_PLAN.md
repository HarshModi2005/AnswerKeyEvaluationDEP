# Faculty Dashboard Implementation Plan

## 1. Fix Missing Components
The following components appear to be empty and need to be implemented to ensure the base design system works:
- `src/components/ui/Sidebar.jsx`
- `src/pages/dashboard-overview/components/MetricsCard.jsx`

## 2. Create Faculty Dashboard Page
**Path:** `src/pages/faculty-dashboard/index.jsx`
**Features:**
- Layout using `Header` and `Sidebar`.
- Grid display of "My Courses".
- Mock data for courses (Code, Title, Semester, Enrolled Students).

## 3. Create Course Card Component
**Path:** `src/pages/faculty-dashboard/components/CourseCard.jsx`
**Design:**
- Clean card design using `bg-surface`.
- Course code validation pill.
- Student count and assignment count indicators.
- Hover effects for interactivity.

## 4. Create Course Detail Page
**Path:** `src/pages/course-detail/index.jsx`
**Features:**
- layout matching `DashboardOverview`.
- Route parameter for `courseId`.
- Course breadcrumbs.
- Tabs for "Overview", "Students", "Assessments", "Settings".
- Mock data for course specifics.

## 5. Update Routing
**Path:** `src/Routes.jsx`
**Changes:**
- Add route `/faculty-dashboard`.
- Add route `/course/:courseId`.
- (Optional) Redirect `/` to `/faculty-dashboard` for this user persona.

## 6. Sidebar Update
- Ensure `Sidebar` includes links to "My Courses" (pointing to `/faculty-dashboard`).

## Design & Style
- Use Tailwind colors from config (`primary`, `secondary`, `surface`).
- Use `AppIcon` for consistent iconography.
- Maintain the "premium" look with shadows, rounded corners, and subtle transitions.
