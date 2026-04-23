import { useState, useEffect } from 'react';
import { FileText, Download, Loader2, FileDown, Eye, RefreshCw } from 'lucide-react';
import { apiFetch, API_BASE } from '../api';

const ReportExport = () => {
    const [format, setFormat] = useState<'html' | 'pdf'>('html');
    const [loading, setLoading] = useState(false);
    const [preview, setPreview] = useState<any>(null);
    const [error, setError] = useState('');
    const [reportData, setReportData] = useState<any>(null);

    useEffect(() => {
        buildReportData();
    }, []);

    const buildReportData = async () => {
        try {
            const txData = await apiFetch('/ingestion/transactions/all');
            const portData = await apiFetch('/investments/portfolio');

            let spending_chart: Record<string, number> = {};
            let totalExpenses = 0;

            const transactions = txData.data || [];
            for (const tx of transactions) {
                if (tx.category === 'Income') continue;
                const cat = tx.category || 'Uncategorized';
                spending_chart[cat] = (spending_chart[cat] || 0) + tx.amount;
                totalExpenses += tx.amount;
            }

            if (Object.keys(spending_chart).length === 0) {
                // leave empty
            }

            let portfolio = portData.portfolio || [];

            let recommendations: string[] = [];
            try {
                const recData = await apiFetch('/recommendations/generate-auto');
                recommendations = recData.recommendations || [];
            } catch {
                // skip
            }

            if (recommendations.length === 0) {
                // leave empty
            }

            // Real income logic (fetch from transactions if not passed, or compute)
            let income = 0;
            for (const tx of transactions) {
                if (tx.category === 'Income') income += tx.amount;
            }
            const data = {
                title: 'Monthly Financial Report',
                start_date: '2024-03-01',
                end_date: '2024-03-31',
                income,
                expenses: totalExpenses,
                spending_chart,
                recommendations,
                portfolio,
            };

            setReportData(data);
        } catch {
            setReportData(null);
            setError('Could not generate report with live data.');
        }
    };

    const handlePreview = async () => {
        if (!reportData) return;
        setLoading(true);
        setError('');
        try {
            const data = await apiFetch('/reports/generate', {
                method: 'POST',
                body: JSON.stringify(reportData),
            });
            setPreview(data.report);
        } catch {
            setError('Failed to preview. API Error.');
        } finally {
            setLoading(false);
        }
    };

    const handleExport = async () => {
        if (!reportData) return;
        setLoading(true);
        setError('');

        try {
            const token = localStorage.getItem('finsight_token');
            const headers: Record<string, string> = { 'Content-Type': 'application/json' };
            if (token) headers['Authorization'] = `Bearer ${token}`;

            const response = await fetch(`${API_BASE}/reports/export/${format}`, {
                method: 'POST',
                headers,
                body: JSON.stringify(reportData),
            });

            if (!response.ok) {
                throw new Error('Failed to export');
            }

            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `finsight_report_${new Date().getTime()}.${format}`;
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            a.remove();
        } catch {
            setError(`Failed to export ${format.toUpperCase()}`);
        } finally {
            setLoading(false);
        }
    };

    const dataReady = !!reportData;
    const totalExpenses = reportData ? reportData.expenses : 0;

    return (
        <div className="space-y-6">
            <div className="bg-neutral-900/50 backdrop-blur-xl border border-white/5 rounded-2xl p-6">
                <div className="flex items-center justify-between mb-6">
                    <div className="flex items-center gap-3">
                        <FileText size={22} className="text-purple-400" />
                        <h3 className="text-xl font-bold">Monthly Report</h3>
                    </div>
                    <button
                        onClick={buildReportData}
                        className="text-xs bg-neutral-800 text-neutral-300 px-3 py-1.5 rounded-lg border border-white/5 hover:border-white/10 hover:bg-neutral-700 transition-all flex items-center gap-1.5"
                    >
                        <RefreshCw size={12} />
                        Refresh Data
                    </button>
                </div>

                <p className="text-sm text-neutral-400 mb-4">
                    Generate a comprehensive financial report with spending charts, category breakdowns,
                    savings recommendations, and portfolio summary.
                </p>

                {dataReady && (
                    <div className="grid grid-cols-3 gap-3 mb-6">
                        <div className="bg-neutral-900/50 rounded-xl p-3 text-center">
                            <div className="text-[10px] text-neutral-500 uppercase tracking-wider">Income</div>
                            <div className="text-sm font-bold text-emerald-400 mt-1">
                                ${reportData.income.toLocaleString()}
                            </div>
                        </div>
                        <div className="bg-neutral-900/50 rounded-xl p-3 text-center">
                            <div className="text-[10px] text-neutral-500 uppercase tracking-wider">Expenses</div>
                            <div className="text-sm font-bold text-rose-400 mt-1">
                                ${totalExpenses.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
                            </div>
                        </div>
                        <div className="bg-neutral-900/50 rounded-xl p-3 text-center">
                            <div className="text-[10px] text-neutral-500 uppercase tracking-wider">Categories</div>
                            <div className="text-sm font-bold text-indigo-400 mt-1">
                                {Object.keys(reportData.spending_chart || {}).length}
                            </div>
                        </div>
                    </div>
                )}

                <div className="flex gap-3 mb-6">
                    <button
                        onClick={() => setFormat('html')}
                        className={`flex-1 py-3 px-4 rounded-xl text-sm font-medium transition-all duration-200 border ${format === 'html'
                            ? 'bg-indigo-500/20 border-indigo-500/40 text-indigo-300'
                            : 'bg-neutral-900/50 border-white/5 text-neutral-400 hover:border-white/10'
                            }`}
                    >
                        <FileDown size={16} className="inline mr-2" />
                        HTML
                    </button>
                    <button
                        onClick={() => setFormat('pdf')}
                        className={`flex-1 py-3 px-4 rounded-xl text-sm font-medium transition-all duration-200 border ${format === 'pdf'
                            ? 'bg-indigo-500/20 border-indigo-500/40 text-indigo-300'
                            : 'bg-neutral-900/50 border-white/5 text-neutral-400 hover:border-white/10'
                            }`}
                    >
                        <FileDown size={16} className="inline mr-2" />
                        PDF
                    </button>
                </div>

                {error && (
                    <div className="mb-4 text-sm text-rose-400 bg-rose-500/10 p-3 rounded-lg border border-rose-500/20">
                        {error}
                    </div>
                )}

                <div className="flex gap-3">
                    <button
                        onClick={handlePreview}
                        disabled={loading || !dataReady}
                        className="flex-1 flex items-center justify-center gap-2 bg-neutral-800 text-white font-semibold rounded-xl py-3 hover:bg-neutral-700 transition-all disabled:opacity-50"
                    >
                        {loading ? <Loader2 size={18} className="animate-spin" /> : <Eye size={18} />}
                        Preview
                    </button>
                    <button
                        onClick={handleExport}
                        disabled={loading || !dataReady}
                        className="flex-1 flex items-center justify-center gap-2 bg-indigo-500 text-white font-semibold rounded-xl py-3 hover:bg-indigo-400 transition-all disabled:opacity-50"
                    >
                        {loading ? <Loader2 size={18} className="animate-spin" /> : <Download size={18} />}
                        Export
                    </button>
                </div>
            </div>

            {preview && (
                <div className="bg-neutral-900/80 backdrop-blur-xl border border-white/5 rounded-2xl p-6 relative">
                    <button
                        onClick={() => setPreview(null)}
                        className="absolute top-4 right-4 text-neutral-500 hover:text-white"
                    >
                        x
                    </button>
                    <h4 className="text-xl font-bold mb-2">{preview.header || 'Report Preview'}</h4>
                    <p className="text-neutral-400 text-sm mb-6">{preview.date_range}</p>
                    <div className="space-y-4">
                        <div className="p-4 bg-neutral-800/50 rounded-xl">
                            <h5 className="font-bold mb-2">Summary</h5>
                            <div className="grid grid-cols-2 gap-2 text-sm">
                                <span className="text-neutral-400">Income:</span>
                                <span className="text-emerald-400">${preview.summary?.income}</span>
                                <span className="text-neutral-400">Expenses:</span>
                                <span className="text-rose-400">${preview.summary?.expenses}</span>
                                <span className="text-neutral-400">Savings:</span>
                                <span className="text-indigo-400">${preview.summary?.savings}</span>
                            </div>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
};
export default ReportExport;
