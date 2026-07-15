import { useState, useEffect } from 'react';
import { useQueryClient } from '@tanstack/react-query';
import { Minus, Plus, Save } from 'lucide-react';
import { useToast } from '@/contexts/ToastContext';
import { useApp } from '@/contexts/AppContext';
import api from '@/lib/apiClient';

export default function ManageAcademicYear() {
  const { addToast } = useToast();
  const queryClient = useQueryClient();
  const { currentAcademicYear } = useApp();
  
  const [yearLabel, setYearLabel] = useState<number | null>(null);
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    if (currentAcademicYear) {
      const parsed = parseInt(currentAcademicYear, 10);
      if (!isNaN(parsed)) {
        setYearLabel(parsed);
      }
    }
  }, [currentAcademicYear]);

  const handleDecrease = () => {
    if (yearLabel !== null) {
      setYearLabel(prev => (prev ? prev - 1 : prev));
    }
  };

  const handleIncrease = () => {
    if (yearLabel !== null) {
      setYearLabel(prev => (prev ? prev + 1 : prev));
    }
  };

  const handleSave = async () => {
    if (yearLabel === null) return;
    setSaving(true);
    try {
      await api.patch('/academic-years/current/label', {
        year_label: yearLabel.toString()
      });
      addToast('success', 'Academic year updated successfully');
      queryClient.invalidateQueries({ queryKey: ['current-academic-year'] });
      queryClient.invalidateQueries({ queryKey: ['dashboard-summary'] });
      queryClient.invalidateQueries({ queryKey: ['classes'] });
      queryClient.invalidateQueries({ queryKey: ['students'] });
    } catch (err: any) {
      addToast('error', err?.data?.detail || 'Failed to update academic year');
    } finally {
      setSaving(false);
    }
  };

  if (!currentAcademicYear) {
    return <div className="p-8 text-center text-slate-500">Loading...</div>;
  }

  return (
    <div className="max-w-2xl mx-auto space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold text-slate-800 dark:text-white">Academic Year</h1>
      </div>

      <div className="bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-xl p-8 text-center space-y-6">
        <p className="text-slate-500 dark:text-slate-400">
          Update the current academic year label. This only updates the year label and does not modify any classes, students, promotion rules, or attendance.
        </p>

        <div className="flex justify-center items-center gap-6">
          <button 
            onClick={handleDecrease}
            className="p-3 rounded-full bg-slate-100 dark:bg-slate-700 hover:bg-slate-200 dark:hover:bg-slate-600 transition-colors"
          >
            <Minus className="w-6 h-6 text-slate-600 dark:text-slate-300" />
          </button>

          <div className="text-4xl font-bold text-slate-800 dark:text-white w-32 text-center">
            {yearLabel !== null ? yearLabel : '--'}
          </div>

          <button 
            onClick={handleIncrease}
            className="p-3 rounded-full bg-slate-100 dark:bg-slate-700 hover:bg-slate-200 dark:hover:bg-slate-600 transition-colors"
          >
            <Plus className="w-6 h-6 text-slate-600 dark:text-slate-300" />
          </button>
        </div>

        <div className="pt-4">
          <button 
            onClick={handleSave}
            disabled={saving || yearLabel === null || yearLabel.toString() === currentAcademicYear}
            className="flex items-center gap-2 mx-auto px-8 py-3 bg-emerald-500 hover:bg-emerald-600 text-white rounded-lg font-medium transition-colors disabled:opacity-50"
          >
            <Save className="w-5 h-5" />
            {saving ? 'Saving...' : 'Save'}
          </button>
        </div>
      </div>
    </div>
  );
}
