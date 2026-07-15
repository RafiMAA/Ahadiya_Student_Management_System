import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { Search, Eye, Plus } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { useToast } from '@/contexts/ToastContext';
import { useQueryClient } from '@tanstack/react-query';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import api from '@/lib/apiClient';
import type { Student } from '@/types';

const graduationYears = [2025, 2024, 2023, 2022, 2021, 2020];

export default function Alumni() {
  const navigate = useNavigate();
  
  const [search, setSearch] = useState('');
  const [yearFilter, setYearFilter] = useState('');
  const [page, setPage] = useState(1);
  const { addToast } = useToast();
  const queryClient = useQueryClient();

  const [showAdd, setShowAdd] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [form, setForm] = useState({
    fullName: '', gender: 'Male' as 'Male' | 'Female', dateOfBirth: '',
    parentName: '', parentContact: '', ownContact: '',
    medium: 'Sinhala' as 'Sinhala' | 'Tamil', joinedDate: '', graduationYear: ''
  });

  const buildUrl = () => {
    let url = `/students?status=Alumni&page=${page}&page_size=10`;
    if (search) url += `&search=${encodeURIComponent(search)}`;
    return url;
  };

  const { data, isLoading: loading } = useQuery({
    queryKey: ['alumni', page, search],
    queryFn: () => api.get<{items: Student[], total: number, total_pages: number}>(buildUrl()),
  });

  const allAlumni = data?.items || [];
  const alumni = yearFilter ? allAlumni.filter(i => i.graduation_year === yearFilter) : allAlumni;
  const totalRecords = data?.total || 0;
  const totalPages = data?.total_pages || 1;

  const handleFilterChange = (setter: any, val: string) => {
    setter(val);
    setPage(1);
  };

  const handleAdd = async (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitting(true);
    try {
      await api.post('/students/alumni', {
        full_name: form.fullName,
        gender: form.gender,
        date_of_birth: form.dateOfBirth,
        parent_name: form.parentName,
        parent_contact: form.parentContact,
        own_contact: form.ownContact || undefined,
        medium: form.medium,
        joined_date: form.joinedDate,
        graduation_year: form.graduationYear
      });
      addToast('success', 'Alumni added successfully');
      setShowAdd(false);
      queryClient.invalidateQueries({ queryKey: ['alumni'] });
      setForm({
        fullName: '', gender: 'Male', dateOfBirth: '',
        parentName: '', parentContact: '', ownContact: '',
        medium: 'Sinhala', joinedDate: '', graduationYear: ''
      });
    } catch (err: any) {
      addToast('error', err?.data?.detail || 'Failed to add alumni');
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="space-y-4">
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div className="flex items-center gap-4 w-full sm:w-auto flex-1">
          <div className="relative w-full sm:w-72">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
          <input
            type="text"
            placeholder="Search alumni..."
            value={search}
            onChange={e => handleFilterChange(setSearch, e.target.value)}
            className="w-full pl-9 pr-3 py-2 border border-slate-200 dark:border-slate-700 rounded-lg bg-white dark:bg-slate-800 text-slate-900 dark:text-white text-sm focus:ring-2 focus:ring-emerald-500 outline-none"
          />
        </div>
        <select
          value={yearFilter}
          onChange={e => handleFilterChange(setYearFilter, e.target.value)}
          className="px-3 py-2 border border-slate-200 dark:border-slate-700 rounded-lg bg-white dark:bg-slate-800 text-sm text-slate-900 dark:text-white focus:ring-2 focus:ring-emerald-500 outline-none"
        >
          <option value="">All Years</option>
          {graduationYears.map(y => <option key={y} value={y.toString()}>{y}</option>)}
        </select>
        </div>
        <button onClick={() => setShowAdd(true)} className="w-full sm:w-auto px-4 py-2 bg-emerald-600 hover:bg-emerald-700 text-white text-sm font-medium rounded-lg flex items-center justify-center gap-2 transition-colors">
          <Plus className="w-4 h-4" /> Add Alumni
        </button>
      </div>

      <div className="bg-white dark:bg-slate-900 rounded-xl border border-slate-200 dark:border-slate-700 shadow-sm overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800">
                <th className="text-left text-xs font-semibold text-slate-500 dark:text-slate-400 px-4 py-3">Reg No.</th>
                <th className="text-left text-xs font-semibold text-slate-500 dark:text-slate-400 px-4 py-3">Name</th>
                <th className="text-left text-xs font-semibold text-slate-500 dark:text-slate-400 px-4 py-3">Gender</th>
                <th className="text-left text-xs font-semibold text-slate-500 dark:text-slate-400 px-4 py-3">Last Class</th>
                <th className="text-left text-xs font-semibold text-slate-500 dark:text-slate-400 px-4 py-3">Medium</th>
                <th className="text-center text-xs font-semibold text-slate-500 dark:text-slate-400 px-4 py-3">Graduation Year</th>
                <th className="text-center text-xs font-semibold text-slate-500 dark:text-slate-400 px-4 py-3">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 dark:divide-slate-800">
              {loading ? (
                <tr><td colSpan={7} className="text-center py-12"><div className="animate-spin rounded-full h-6 w-6 border-b-2 border-emerald-600 mx-auto" /></td></tr>
              ) : alumni.map(student => (
                <tr key={student.id} className="hover:bg-slate-50 dark:hover:bg-slate-800/50">
                  <td className="px-4 py-3 text-sm text-slate-500 font-mono">{student.registration_number}</td>
                  <td className="px-4 py-3 text-sm font-medium text-slate-900 dark:text-white">{student.full_name}</td>
                  <td className="px-4 py-3 text-sm text-slate-600 dark:text-slate-400">{student.gender}</td>
                  <td className="px-4 py-3 text-sm text-slate-600 dark:text-slate-400">{student.class_name || 'N/A'}</td>
                  <td className="px-4 py-3 text-sm text-slate-600 dark:text-slate-400">{student.medium}</td>
                  <td className="px-4 py-3 text-center">
                    <span className="inline-block px-2 py-0.5 rounded-full text-xs font-medium bg-blue-50 text-blue-700 dark:bg-blue-900/20 dark:text-blue-400">
                      {student.graduation_year || 'Unknown'}
                    </span>
                  </td>
                  <td className="px-4 py-3 text-center">
                    <button onClick={() => navigate(`/students/${student.id}`)} className="p-1.5 rounded-lg hover:bg-slate-100 dark:hover:bg-slate-700 text-slate-500 transition-colors">
                      <Eye className="w-4 h-4" />
                    </button>
                  </td>
                </tr>
              ))}
              {!loading && alumni.length === 0 && (
                <tr><td colSpan={7} className="text-center py-12 text-slate-400 dark:text-slate-500 text-sm">No alumni found</td></tr>
              )}
            </tbody>
          </table>
        </div>
        {totalPages > 1 && (
          <div className="flex items-center justify-between px-4 py-3 border-t border-slate-200 dark:border-slate-700">
            <p className="text-xs text-slate-500 dark:text-slate-400">Showing {((page - 1) * 10) + 1} to {Math.min(page * 10, totalRecords)} of {totalRecords}</p>
            <div className="flex gap-1">
              <button onClick={() => setPage(p => Math.max(1, p - 1))} disabled={page === 1} className="px-3 py-1 text-xs border rounded hover:bg-slate-50 disabled:opacity-50 dark:border-slate-700 dark:text-slate-300">Prev</button>
              {Array.from({ length: totalPages }, (_, i) => (
                <button key={i} onClick={() => setPage(i + 1)} className={`px-3 py-1 text-xs border rounded ${page === i + 1 ? 'bg-emerald-600 text-white border-emerald-600' : 'hover:bg-slate-50 dark:border-slate-700 dark:text-slate-300'}`}>{i + 1}</button>
              ))}
              <button onClick={() => setPage(p => Math.min(totalPages, p + 1))} disabled={page === totalPages} className="px-3 py-1 text-xs border rounded hover:bg-slate-50 disabled:opacity-50 dark:border-slate-700 dark:text-slate-300">Next</button>
            </div>
          </div>
        )}
      </div>

      <Dialog open={showAdd} onOpenChange={setShowAdd}>
        <DialogContent className="max-w-xl">
          <DialogHeader>
            <DialogTitle>Add Alumni</DialogTitle>
          </DialogHeader>
          <form onSubmit={handleAdd} className="mt-4 grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="col-span-2">
              <label className="block text-xs font-medium text-slate-500 mb-1">Full Name *</label>
              <input type="text" value={form.fullName} onChange={e => setForm({...form, fullName: e.target.value})} className="w-full px-3 py-2 border rounded-lg bg-white dark:bg-slate-800" required />
            </div>
            <div>
              <label className="block text-xs font-medium text-slate-500 mb-1">Gender *</label>
              <select value={form.gender} onChange={e => setForm({...form, gender: e.target.value as any})} className="w-full px-3 py-2 border rounded-lg bg-white dark:bg-slate-800">
                <option value="Male">Male</option>
                <option value="Female">Female</option>
              </select>
            </div>
            <div>
              <label className="block text-xs font-medium text-slate-500 mb-1">Date of Birth *</label>
              <input type="date" value={form.dateOfBirth} onChange={e => setForm({...form, dateOfBirth: e.target.value})} className="w-full px-3 py-2 border rounded-lg bg-white dark:bg-slate-800" required />
            </div>
            <div>
              <label className="block text-xs font-medium text-slate-500 mb-1">Parent's Name *</label>
              <input type="text" value={form.parentName} onChange={e => setForm({...form, parentName: e.target.value})} className="w-full px-3 py-2 border rounded-lg bg-white dark:bg-slate-800" required />
            </div>
            <div>
              <label className="block text-xs font-medium text-slate-500 mb-1">Parent's Contact *</label>
              <input type="text" value={form.parentContact} onChange={e => setForm({...form, parentContact: e.target.value})} className="w-full px-3 py-2 border rounded-lg bg-white dark:bg-slate-800" required />
            </div>
            <div>
              <label className="block text-xs font-medium text-slate-500 mb-1">Own Contact</label>
              <input type="text" value={form.ownContact} onChange={e => setForm({...form, ownContact: e.target.value})} className="w-full px-3 py-2 border rounded-lg bg-white dark:bg-slate-800" placeholder="Optional" />
            </div>
            <div>
              <label className="block text-xs font-medium text-slate-500 mb-1">Medium *</label>
              <select value={form.medium} onChange={e => setForm({...form, medium: e.target.value as any})} className="w-full px-3 py-2 border rounded-lg bg-white dark:bg-slate-800">
                <option value="Sinhala">Sinhala</option>
                <option value="Tamil">Tamil</option>
              </select>
            </div>
            <div>
              <label className="block text-xs font-medium text-slate-500 mb-1">Joined Date *</label>
              <input type="date" value={form.joinedDate} onChange={e => setForm({...form, joinedDate: e.target.value})} className="w-full px-3 py-2 border rounded-lg bg-white dark:bg-slate-800" required />
            </div>
            <div>
              <label className="block text-xs font-medium text-slate-500 mb-1">Graduated Year *</label>
              <input type="text" value={form.graduationYear} onChange={e => setForm({...form, graduationYear: e.target.value})} className="w-full px-3 py-2 border rounded-lg bg-white dark:bg-slate-800" placeholder="e.g. 2023" required />
            </div>
            <div className="col-span-2 flex justify-end gap-3 pt-4 border-t border-slate-200 dark:border-slate-800 mt-2">
              <button type="button" onClick={() => setShowAdd(false)} className="px-4 py-2 text-sm font-medium border rounded-lg hover:bg-slate-50 dark:hover:bg-slate-800">Cancel</button>
              <button type="submit" disabled={submitting} className="px-4 py-2 text-sm font-medium bg-emerald-600 text-white rounded-lg hover:bg-emerald-700 disabled:opacity-50">Save Alumni</button>
            </div>
          </form>
        </DialogContent>
      </Dialog>
    </div>
  );
}
