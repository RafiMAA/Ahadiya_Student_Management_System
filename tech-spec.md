# Ahadiya School Management System — Technical Specification

## Dependencies

### Production
| Package | Version | Purpose |
|---------|---------|---------|
| react | ^18.3.0 | UI framework |
| react-dom | ^18.3.0 | DOM renderer |
| react-router-dom | ^6.28.0 | Multi-page routing (14 pages) |
| tailwindcss | ^3.4.0 | Utility CSS |
| @tailwindcss/forms | ^0.5.0 | Form element reset styles |
| lucide-react | ^0.460.0 | Icons (Students, BookOpen, CheckCircle, XCircle, GraduationCap, LayoutDashboard, Calendar, Bell, Moon, Sun, Upload, Download, FileSpreadsheet, etc.) |
| recharts | ^2.13.0 | Charts (Dashboard attendance ring, attendance trends) |
| date-fns | ^3.6.0 | Date utilities (Sunday picker, formatting, month pickers) |
| xlsx | ^0.18.5 | Excel parsing for Step 2-3 of import wizard |
| file-saver | ^2.0.5 | Excel template download trigger |

### Dev
| Package | Version | Purpose |
|---------|---------|---------|
| typescript | ^5.6.0 | Type safety |
| vite | ^5.4.0 | Build tool |
| @vitejs/plugin-react | ^4.3.0 | React Fast Refresh |
| autoprefixer | ^10.4.0 | CSS vendor prefixes |
| postcss | ^8.4.0 | CSS processing |
| @types/react | ^18.3.0 | React type defs |
| @types/react-dom | ^18.3.0 | ReactDOM type defs |
| @types/file-saver | ^2.0.7 | file-saver type defs |

---

## Component Inventory

### Layout (shared across all pages)
| Component | Source | Reuse | Notes |
|-----------|--------|-------|-------|
| Sidebar | Custom | Global | Collapsible on mobile; navigation groups with expand/collapse; active state with left emerald border; fixed left w-64 |
| Header | Custom | Global | Sticky top bar; breadcrumb; dark mode toggle; notification bell; user avatar dropdown |
| AppLayout | Custom | Global | Wraps Sidebar + Header + MainContent; handles mobile sidebar overlay |
| PageContainer | Custom | Global | Consistent padding, bg, scroll behavior for main content area |

### Reusable UI Components
| Component | Source | Used By | Notes |
|-----------|--------|---------|-------|
| StatCard | Custom | Dashboard | Colored top-border stat card with large metric |
| StatusBadge | Custom | StudentList, ClassList, AttendanceHistory | Active/Alumni/Inactive/Submitted color variants |
| DataTable | Custom | StudentList, AttendanceHistory, Teachers, AuditLogs | Generic paginated table (10 rows default); column definition via props |
| Pagination | Custom | DataTable | Page controls with prev/next/jump |
| SearchableSelect | Custom | All forms with dropdowns | shadcn-style select with typeahead search filtering |
| ConfirmDialog | Custom | All delete actions, ConfirmPromotion | Reusable confirmation modal with danger/warning variants |
| ToastNotification | Custom | All pages | Global toast system via context; success/error/info variants |
| EmptyState | Custom | All list views | Illustration + message when no data; uses Islamic SVG watermark |
| LoadingSkeleton | Custom | All data tables | Pulse animation skeleton for table rows |
| SlideOver | Custom | AttendanceHistory | Right-side drawer for detail views |
| StepWizard | Custom | ExcelImport | 4-step progress indicator with step content slots |
| AttendanceToggle | Custom | MarkAttendance | Dual Present/Absent toggle button pair |
| CircularProgress | Custom | Dashboard | SVG ring with stroke-dasharray; green/amber/red thresholds |
| IslamicPatternBG | Custom | Login, EmptyState | SVG pattern component (8-pointed star geometry) |
| Breadcrumb | Custom | Header | Auto-generated from route path |

### Page Sections
| Page | Sections |
|------|----------|
| Login | LoginCard with IslamicPatternBG |
| Dashboard | StatsRow, AttendanceSummary (CircularProgress + details), CompletionTracker, ClassAttendanceGrid |
| MarkAttendance | FilterBar, ActionBar, StudentAttendanceTable, SubmitFooter |
| AttendanceHistory | FilterBar, HistoryTable, SlideOver (detail drawer) |
| StudentList | Toolbar (Search + Filters + AddBtn), StudentTable, Pagination |
| AddStudent | StudentForm (2-col grid, all fields with validation) |
| StudentProfile | ProfileHeader, DetailGrid, Tabs (AttendanceHistory / TransferHistory) |
| Alumni | Same as StudentList with Alumni filter + GraduationYear column |
| ClassList | ClassGrid (cards with type badges, student counts, teacher) |
| CreateClass | ClassForm (grade, medium, gender type, teacher assignment) |
| ExcelImport | StepWizard wrapping 4 step components |
| PromotionRules | RulesTable (From Class → Male/Female targets) |
| PromotionPreview | PreviewTable, Grade11AlumniSection, ConfirmDialog |
| Teachers | TeacherTable, AddTeacher button |
| AuditLogs | LogTable, FilterBar (action type + date range) |

### Hooks
| Hook | Purpose |
|------|---------|
| useLocalStorage | Persist dark mode preference, sidebar collapsed state |
| useToast | Global toast trigger (success/error/info) via context |
| usePagination | Shared pagination logic (page, pageSize, total, slice data) |
| useDebounce | Debounce search input in StudentList |
| useAttendanceCompletion | Track which classes have submitted attendance |
| useStudentFilters | Filter students by grade, medium, gender, status |

---

## Animation Implementation

| Animation | Library | Implementation Approach | Complexity |
|-----------|---------|------------------------|------------|
| Sidebar hover transitions | Tailwind CSS | `transition-colors duration-150 ease-in-out` on nav items | Low |
| Button press feedback | Tailwind CSS | `active:scale-95` utility class | Low |
| Toast entrance/exit | Tailwind CSS | `animate-in slide-in-from-top-2 fade-in duration-200` + `animate-out` via data attributes | Low |
| Modal/dialog overlay | Tailwind CSS | `backdrop-blur-sm bg-black/50` with `opacity-0 → opacity-100` transition | Low |
| Mobile sidebar slide | Tailwind CSS | `translate-x-[-100%]` to `translate-x-0` with `transition-transform duration-300` | Low |
| Skeleton pulse loading | Tailwind CSS | `animate-pulse` utility on skeleton divs | Low |
| CircularProgress ring fill | Inline SVG + CSS | SVG `<circle>` with `stroke-dasharray` and `stroke-dashoffset` animated via CSS transition on mount | Low |
| Slide-over drawer | Tailwind CSS | `translate-x-full` to `translate-x-0` with `transition-transform duration-300` | Low |
| Attendance toggle state | Tailwind CSS | `transition-colors duration-200` on toggle buttons | Low |
| Step wizard progress | Tailwind CSS | Width transition on progress bar + opacity transition on step content | Low |
| Page transitions | Tailwind CSS | `opacity-0 → opacity-100` on route change via React Router outlet wrapper | Low |
| IslamicPatternBG | Custom SVG | Static SVG `<pattern>` with `patternUnits="userSpaceOnUse"`; no animation, just low opacity rendering | Low |

---

## State & Logic Plan

### 1. Global State (React Context)

**ThemeContext** — Dark/light mode
- `theme: 'light' | 'dark'`
- Persisted via `useLocalStorage`
- Applied as class on `<html>` element; Tailwind `dark:` variants handle styling

**ToastContext** — Global notification system
- Queue of toast objects `{ id, type, message }`
- Auto-dismiss after 4 seconds
- Used across all pages for success/error feedback

**AppContext** — Shared app data
- `currentAcademicYear: number` (default 2025)
- `isSidebarCollapsed: boolean` (desktop)
- `isMobileSidebarOpen: boolean` (mobile overlay)
- `currentUser: User` (mock principal)

### 2. Page-Level State (useState/useReducer)

**Dashboard** — No complex state; derived from mock data. Attendance completion status tracked in AppContext.

**MarkAttendance** — Form-like state per page
- `selectedDate: Date` (Sunday-constrained)
- `selectedClass: string`
- `attendanceMap: Map<studentId, 'present' | 'absent'>`
- `hasExistingSubmission: boolean` (mock check)
- Actions: Mark individual, MarkAllPresent, MarkAllAbsent, Submit
- Validation: Check all students have status before submit; show warning if already submitted

**AttendanceHistory** — Filter + view state
- `filters: { class, month, status }`
- `selectedRecord: AttendanceRecord | null` (triggers SlideOver)

**StudentList** — Complex filter/search/pagination
- `searchQuery: string` (debounced)
- `filters: { grade, medium, gender, status }`
- `pagination: { page, pageSize }`
- `selectedStudent: Student | null` (for actions)
- Derived: `filteredStudents` computed from filters + search

**AddStudent** — Form state with validation
- `formData: StudentFormData`
- `errors: Record<field, string>` (inline validation)
- Dynamic class dropdown: filtered by selected grade + medium
- Submit: validate all required fields, show errors, add to mock data

**ExcelImport** — Wizard step machine
- `currentStep: 1 | 2 | 3 | 4`
- `uploadedFile: File | null`
- `parsedData: ParsedRow[]`
- `errors: ValidationError[]`
- `importResult: { success, count, targetClass }`
- Step transitions validated (can't skip to step 3 without upload)

**PromotionPreview** — Confirmation flow
- `previewData: PromotionRow[]`
- `showConfirmDialog: boolean`
- `confirmText: string` (must type "CONFIRM")
- Submit only enabled when confirmText === "CONFIRM"

### 3. Mock Data Architecture

All data stored in-memory via a `mockDatabase` object exported from `data/mockData.ts`:

```
mockDatabase:
├── students: Student[] (342 items)
├── teachers: Teacher[] (18 items)
├── classes: Class[] (24 items)
├── attendanceRecords: AttendanceRecord[]
├── promotionRules: PromotionRule[]
├── auditLogs: AuditLog[]
└── academicYear: 2025
```

Mutations (add student, submit attendance, promote students) modify this in-memory object. No persistence — refresh resets.

### 4. Routing Structure

```
/login                    → Login page (no layout)
/*                        → AppLayout wrapper
  /dashboard              → Dashboard
  /attendance/mark        → MarkAttendance
  /attendance/history     → AttendanceHistory
  /students               → StudentList
  /students/add           → AddStudent
  /students/:id           → StudentProfile
  /students/alumni        → Alumni
  /classes                → ClassList
  /classes/create         → CreateClass
  /classes/import         → ExcelImport
  /academic-year/rules    → PromotionRules
  /academic-year/preview  → PromotionPreview
  /admin/teachers         → Teachers
  /admin/audit-logs       → AuditLogs
```

Route guards: Admin routes (Teachers, Audit Logs) show conditional rendering based on `isAdmin` flag on currentUser.

### 5. Key Derived Data Patterns

- **Class list for dropdown**: Derived from `classes` filtered by selected grade + medium (cascading dropdowns in AddStudent)
- **Attendance percentage**: `(present / (present + absent)) * 100` — used for badge coloring thresholds
- **Attendance completion status**: Boolean per class per date — used on Dashboard and MarkAttendance
- **Student status counts**: Derived grouping for stat cards on Dashboard

---

## Other Key Decisions

### Why Recharts for Dashboard Ring
Despite the CircularProgress component being implementable with raw SVG, Recharts is included for potential attendance trend charts (line/bar) in future expansions and provides a consistent charting foundation. The circular progress specifically uses inline SVG for performance.

### Excel Parsing Strategy
Use `xlsx` library (SheetJS) for client-side parsing. Parse uploaded `.xlsx` files into JSON in Step 2, validate row-by-row in Step 3, and simulate import in Step 4. No server upload — all in browser.

### PDF Download Buttons
All "Download PDF" buttons are mock-only. They show a "Generating..." loading state (spinner) for 1.5 seconds then trigger a toast notification "PDF downloaded" without actual file generation. No PDF library needed.

### Dark Mode Implementation
Use Tailwind's `darkMode: 'class'` strategy. Toggle class on `<html>`. All color values use `dark:` variants. Sidebar is always dark slate regardless of mode (it's inherently dark).

### Mobile Strategy
- Sidebar collapses to hamburger menu on screens < 1024px
- Tables horizontally scroll with `overflow-x-auto` on mobile
- Stat cards stack to single column on mobile
- Attendance toggle buttons remain large enough for touch targets (min 44px height)
