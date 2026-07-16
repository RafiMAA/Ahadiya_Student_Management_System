import { useState, useEffect } from 'react';
import { FileText, Send, Trash2, Calendar, User, GraduationCap, Clock } from 'lucide-react';
import { useToast } from '@/contexts/ToastContext';
import api from '@/lib/apiClient';
import type { StudentAchievement } from '@/types';

interface Props {
  studentId: string;
}

export default function StudentAchievements({ studentId }: Props) {
  const { addToast } = useToast();
  const [achievements, setAchievements] = useState<StudentAchievement[]>([]);
  const [loading, setLoading] = useState(true);
  const [text, setText] = useState('');
  const [submitting, setSubmitting] = useState(false);

  const fetchAchievements = async () => {
    try {
      const data = await api.get<StudentAchievement[]>(`/students/${studentId}/achievements`);
      setAchievements(data);
    } catch {
      addToast('error', 'Failed to load achievements');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAchievements();
  }, [studentId]);

  const handleAdd = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!text.trim()) return;
    setSubmitting(true);
    try {
      const newAch = await api.post<StudentAchievement>(`/students/${studentId}/achievements`, {
        achievement_text: text.trim(),
      });
      setAchievements(prev => [newAch, ...prev]);
      setText('');
      addToast('success', 'Report added');
    } catch (err: any) {
      addToast('error', err?.data?.detail || 'Failed to add report');
    } finally {
      setSubmitting(false);
    }
  };

  const handleDelete = async (achievementId: string) => {
    if (!confirm('Are you sure you want to delete this report?')) return;
    try {
      await api.delete(`/students/${studentId}/achievements/${achievementId}`);
      setAchievements(prev => prev.filter(a => a.id !== achievementId));
      addToast('success', 'Report deleted');
    } catch (err: any) {
      addToast('error', err?.data?.detail || 'Failed to delete report');
    }
  };

  // Group achievements by academic year
  const grouped = achievements.reduce((acc, ach) => {
    const key = `${ach.academic_year_label}`;
    if (!acc[key]) {
      acc[key] = { year: ach.academic_year_label, grade: ach.grade, items: [] };
    }
    acc[key].items.push(ach);
    return acc;
  }, {} as Record<string, { year: string; grade: number; items: StudentAchievement[] }>);

  const groupedList = Object.values(grouped);

  if (loading) {
    return (
      <div className="flex items-center justify-center py-16">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-emerald-600" />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Add Report Form */}
      <div className="bg-white dark:bg-slate-900 rounded-xl border border-slate-200 dark:border-slate-700 p-5 shadow-sm">
        <h3 className="text-sm font-semibold text-slate-900 dark:text-white flex items-center gap-2 mb-3">
          <FileText className="w-4 h-4 text-amber-500" /> Add Report
        </h3>
        <form onSubmit={handleAdd} className="flex flex-col sm:flex-row gap-3">
          <textarea
            value={text}
            onChange={e => setText(e.target.value)}
            rows={2}
            placeholder="E.g. Year end exam marks: 95%, Ramazan Quran count:3 ,..."
            className="flex-1 px-3 py-2 border border-slate-200 dark:border-slate-700 rounded-lg bg-white dark:bg-slate-800 text-slate-900 dark:text-white text-sm focus:ring-2 focus:ring-emerald-500 outline-none resize-none"
          />
          <button
            type="submit"
            disabled={submitting || !text.trim()}
            className="w-full sm:w-auto sm:self-end flex items-center justify-center gap-2 px-4 py-2.5 bg-emerald-600 hover:bg-emerald-700 disabled:bg-slate-300 dark:disabled:bg-slate-700 text-white font-medium rounded-lg transition-colors text-sm shrink-0"
          >
            <Send className="w-4 h-4" />
            {submitting ? 'Adding...' : 'Add Report'}
          </button>
        </form>
      </div>

      {/* Achievements Timeline */}
      {groupedList.length === 0 ? (
        <div className="text-center py-12 text-slate-400 dark:text-slate-500">
          <FileText className="w-12 h-12 mx-auto mb-3 opacity-30" />
          <p className="text-sm">No reports recorded yet.</p>
          <p className="text-xs mt-1">Add the student's first report above.</p>
        </div>
      ) : (
        <div className="space-y-5">
          {groupedList.map(group => (
            <div key={group.year} className="bg-white dark:bg-slate-900 rounded-xl border border-slate-200 dark:border-slate-700 shadow-sm overflow-hidden">
              {/* Year Header */}
              <div className="px-5 py-3 bg-gradient-to-r from-slate-50 to-slate-100/50 dark:from-slate-800 dark:to-slate-800/50 border-b border-slate-200 dark:border-slate-700 flex items-center gap-3">
                <div className="w-8 h-8 rounded-lg bg-amber-100 dark:bg-amber-900/30 text-amber-600 dark:text-amber-400 flex items-center justify-center">
                  <Calendar className="w-4 h-4" />
                </div>
                <div>
                  <h4 className="text-sm font-bold text-slate-900 dark:text-white">
                    Academic Year {group.year}
                  </h4>
                  <p className="text-xs text-slate-500 dark:text-slate-400 flex items-center gap-1">
                    <GraduationCap className="w-3 h-3" /> Grade {group.grade}
                  </p>
                </div>
              </div>

              {/* Achievement items */}
              <div className="divide-y divide-slate-100 dark:divide-slate-800">
                {group.items.map(ach => (
                  <div key={ach.id} className="px-5 py-3 hover:bg-slate-50/50 dark:hover:bg-slate-800/30 transition-colors group">
                    <div className="flex items-start gap-3">
                      <div className="mt-0.5 w-2 h-2 rounded-full bg-emerald-500 shrink-0" />
                      <div className="flex-1 min-w-0">
                        <p className="text-sm text-slate-800 dark:text-slate-200 whitespace-pre-wrap">
                          {ach.achievement_text}
                        </p>
                        <div className="flex items-center gap-3 mt-1.5 text-xs text-slate-400 dark:text-slate-500">
                          <span className="flex items-center gap-1">
                            <User className="w-3 h-3" /> {ach.created_by_name}
                          </span>
                          <span className="flex items-center gap-1">
                            <Clock className="w-3 h-3" /> {new Date(ach.created_at).toLocaleDateString('en-GB', { day: 'numeric', month: 'short', year: 'numeric' })}
                          </span>
                        </div>
                      </div>
                      {ach.can_delete && (
                        <button
                          onClick={() => handleDelete(ach.id)}
                          className="opacity-0 group-hover:opacity-100 p-1.5 text-red-400 hover:text-red-600 hover:bg-red-50 dark:hover:bg-red-900/20 rounded-lg transition-all"
                          title="Delete report"
                        >
                          <Trash2 className="w-4 h-4" />
                        </button>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
